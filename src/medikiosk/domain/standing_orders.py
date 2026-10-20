"""Pure domain Clinical Standing Orders (CSO) & Pre-Consultation Lab Router engine.

Evaluates presenting symptoms, age, vitals, and triage status to generate
deterministic standing orders for diagnostics before OPD physician consultation.

INVARIANTS:
- Zero I/O, zero network, zero logging, zero external framework imports.
- Pure functions and immutable value objects only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from medikiosk.domain.vitals import VitalSigns


@dataclass(frozen=True)
class LabOrderItem:
    """Immutable standing diagnostic order specification.

    Attributes:
        code: Unique clinical test code (e.g., 'ECG-01', 'LAB-TROP').
        name_en: English test description.
        name_hi: Hindi test description.
        urgency: Clinical urgency ('STAT', 'URGENT', 'ROUTINE').
        bay_room: Hospital wing or room for test collection.
    """

    code: str
    name_en: str
    name_hi: str
    urgency: str
    bay_room: str


@dataclass(frozen=True)
class StandingOrderRecommendation:
    """Immutable collection of standing pre-consultation lab and imaging orders.

    Attributes:
        orders: Ordered tuple of deduplicated lab/imaging items.
        clinical_rationale: Aggregated clinical justification for pre-consultation testing.
        estimated_time_saved_minutes: Total turnaround time saved prior to physician consultation.
        requires_fasting: Whether any recommended test requires a fasting state.
    """

    orders: tuple[LabOrderItem, ...]
    clinical_rationale: str
    estimated_time_saved_minutes: int
    requires_fasting: bool = False


# Pre-defined Standing Diagnostic Orders
ORDER_STAT_ECG = LabOrderItem(
    code="ECG-01",
    name_en="STAT 12-Lead ECG",
    name_hi="तत्काल 12-लीड ईसीजी",
    urgency="STAT",
    bay_room="ECG Bay 1",
)
ORDER_POC_TROPONIN = LabOrderItem(
    code="LAB-TROP",
    name_en="Point-of-Care Troponin-I",
    name_hi="प्वाइंट-ऑफ-केयर ट्रोपोनिन-I",
    urgency="STAT",
    bay_room="Phlebotomy Bay 1",
)
ORDER_CBC_PLATELETS = LabOrderItem(
    code="LAB-CBC",
    name_en="CBC with Platelets",
    name_hi="सीबीसी और प्लेटलेट्स",
    urgency="URGENT",
    bay_room="Phlebotomy Bay 2",
)
ORDER_DENGUE_RAPID = LabOrderItem(
    code="LAB-DENGUE",
    name_en="Dengue NS1 Antigen & IgM Rapid",
    name_hi="डेंगू एनएस1 और आईजीएम",
    urgency="URGENT",
    bay_room="Phlebotomy Bay 2",
)
ORDER_MALARIA_RAPID = LabOrderItem(
    code="LAB-MP",
    name_en="Malaria Antigen Rapid (Pv/Pf)",
    name_hi="मलेरिया एंटीजन रैपिड",
    urgency="URGENT",
    bay_room="Phlebotomy Bay 2",
)
ORDER_DIGITAL_CXR = LabOrderItem(
    code="RAD-CXR",
    name_en="Digital Chest X-Ray PA View",
    name_hi="डिजिटल चेस्ट एक्स-रे",
    urgency="URGENT",
    bay_room="Radiology Room 105",
)
ORDER_ABG = LabOrderItem(
    code="LAB-ABG",
    name_en="Arterial Blood Gas (ABG)",
    name_hi="धमनी रक्त गैस",
    urgency="STAT",
    bay_room="Phlebotomy Bay 1",
)
ORDER_CAPILLARY_BG = LabOrderItem(
    code="LAB-CBG",
    name_en="Capillary Blood Glucose (CBG)",
    name_hi="रक्त शर्करा परीक्षण",
    urgency="ROUTINE",
    bay_room="Phlebotomy Bay 2",
)

CARDIAC_PATTERNS = [
    r"\bchest\s+pain\b",
    r"\bseene\s+mein\s+dard\b",
    r"\bchaati\s+mein\s+dard\b",
    r"\bchest\s+pressure\b",
    r"\bpressure\s+in\s+chest\b",
    r"\btightness\b",
    r"\bleft\s+arm\b",
    r"\bjaw\s+pain\b",
    r"\bangina\b",
    r"\bdiaphoresis\b",
    r"\bcardiac\b",
    r"\bheart\s+attack\b",
    r"\bdil\s+ka\s+daura\b",
    r"\bछाती\s+में\s+दर्द\b",
    r"\bसीने\s+में\s+दर्द\b",
]

FEVER_PATTERNS = [
    r"\bfever\b",
    r"\bbukhar\b",
    r"\bhigh\s+temp\b",
    r"\btaap\b",
    r"\bpyrexia\b",
    r"\bchills\b",
    r"\bdengue\b",
    r"\bmalaria\b",
    r"\bबुखार\b",
    r"\bतेज़\s+बुखार\b",
]

RESPIRATORY_PATTERNS = [
    r"\bbreathlessness\b",
    r"\bshortness\s+of\s+breath\b",
    r"\bdyspnea\b",
    r"\bsaans\s+lene\s+mein\s+dikkat\b",
    r"\bsaans\s+phoolna\b",
    r"\bwheezing\b",
    r"\bhypoxia\b",
    r"\bcough\s+with\s+blood\b",
    r"\bसांस\s+फूलना\b",
    r"\bदम\s+फूलना\b",
]


class StandingOrdersEngine:
    """Pure domain engine that computes standing diagnostic lab & radiology orders."""

    @staticmethod
    def _extract_vitals_data(
        vitals: VitalSigns | dict[str, Any] | None,
    ) -> tuple[float | None, int | None, int | None]:
        """Extract temperature_c, spo2_percent, respiration_rate from vitals input."""
        if vitals is None:
            return None, None, None

        if isinstance(vitals, VitalSigns):
            return vitals.temperature_c, vitals.spo2_percent, vitals.respiration_rate

        temp = vitals.get("temperature_c", vitals.get("temperature"))
        spo2 = vitals.get("spo2_percent", vitals.get("spo2"))
        resp = vitals.get("respiration_rate", vitals.get("respiration"))

        temp_f = float(temp) if temp is not None else None
        spo2_i = int(spo2) if spo2 is not None else None
        resp_i = int(resp) if resp is not None else None
        return temp_f, spo2_i, resp_i

    @classmethod
    def evaluate(
        cls,
        symptoms_text: str | list[str],
        age: int | None = None,
        vitals: VitalSigns | dict[str, Any] | None = None,
        triage_priority: str | None = None,
    ) -> StandingOrderRecommendation:
        """Evaluate clinical presentation and generate standing lab and imaging recommendations.

        Rules:
        1. Cardiac / Chest Pain / Red Veto:
           - STAT 12-Lead ECG + PoC Troponin-I (saves 45 min).
        2. Acute Febrile Illness (Temp >= 38.0 C or fever keywords):
           - CBC with Platelets + Dengue NS1/IgM + Malaria Rapid (saves 60 min).
        3. Respiratory Distress / Hypoxia (SpO2 <= 94% or RR >= 22 or dyspnea keywords):
           - Digital Chest X-Ray + Arterial Blood Gas (saves 40 min).
        4. Routine / Metabolic Screening (Age >= 45):
           - Capillary Blood Glucose (saves 15 min).
        """
        if isinstance(symptoms_text, list):
            joined_text = " ".join(symptoms_text).lower()
        else:
            joined_text = (symptoms_text or "").lower()

        temp_c, spo2_percent, resp_rate = cls._extract_vitals_data(vitals)

        orders_list: list[LabOrderItem] = []
        rationales: list[str] = []
        time_saved = 0

        # Check Cardiac / Chest Pain / Red Veto
        has_cardiac_symptom = any(re.search(pat, joined_text) for pat in CARDIAC_PATTERNS)
        is_red_triage = triage_priority is not None and triage_priority.upper() in (
            "RED",
            "CRITICAL",
            "CARDIAC_RED_FLAG",
        )

        if has_cardiac_symptom or (
            is_red_triage and ("chest" in joined_text or "pain" in joined_text or not joined_text)
        ):
            orders_list.extend([ORDER_STAT_ECG, ORDER_POC_TROPONIN])
            rationales.append(
                "Suspected acute coronary syndrome: STAT ECG and cardiac biomarkers indicated"
            )
            time_saved += 45

        # Check Acute Fever (Temp >= 38.0 C or fever keywords)
        has_fever_temp = temp_c is not None and temp_c >= 38.0
        has_fever_symptom = any(re.search(pat, joined_text) for pat in FEVER_PATTERNS)

        if has_fever_temp or has_fever_symptom:
            orders_list.extend([ORDER_CBC_PLATELETS, ORDER_DENGUE_RAPID, ORDER_MALARIA_RAPID])
            rationales.append(
                "Acute febrile illness protocol: complete blood count, "
                "dengue NS1/IgM, and malaria rapid testing"
            )
            time_saved += 60

        # Check Respiratory Distress / Hypoxia (SpO2 <= 94% or RR >= 22 or keywords)
        has_hypoxia = spo2_percent is not None and spo2_percent <= 94
        has_tachypnea = resp_rate is not None and resp_rate >= 22
        has_respiratory_symptom = any(re.search(pat, joined_text) for pat in RESPIRATORY_PATTERNS)

        if has_hypoxia or has_tachypnea or has_respiratory_symptom:
            orders_list.extend([ORDER_DIGITAL_CXR, ORDER_ABG])
            rationales.append(
                "Acute respiratory compromise protocol: digital chest radiography "
                "and arterial blood gas analysis"
            )
            time_saved += 40

        # Check Routine / Metabolic Screening for age >= 45
        if age is not None and age >= 45:
            orders_list.append(ORDER_CAPILLARY_BG)
            rationales.append(
                "Age-appropriate metabolic screening (age >= 45): Capillary blood glucose"
            )
            time_saved += 15

        if not orders_list:
            return StandingOrderRecommendation(
                orders=(),
                clinical_rationale=(
                    "No standing pre-consultation orders indicated "
                    "based on presenting symptoms and vitals."
                ),
                estimated_time_saved_minutes=0,
                requires_fasting=False,
            )

        # Deduplicate orders preserving encounter order
        seen_codes: set[str] = set()
        deduped_orders: list[LabOrderItem] = []
        for order in orders_list:
            if order.code not in seen_codes:
                seen_codes.add(order.code)
                deduped_orders.append(order)

        return StandingOrderRecommendation(
            orders=tuple(deduped_orders),
            clinical_rationale="; ".join(rationales),
            estimated_time_saved_minutes=time_saved,
            requires_fasting=False,
        )
