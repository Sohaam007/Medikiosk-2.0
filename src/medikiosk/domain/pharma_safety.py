"""Pure domain Pharmacovigilance Drug-Drug Interaction (DDI) & Safety Firewall Engine.

Evaluates prescribed medications against existing prescription history (OCR),
declared patient allergies, objective physiological vitals, and presenting syndromes.

INVARIANTS:
- Zero I/O, zero network, zero logging, zero framework imports.
- Pure functions and immutable value objects only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from medikiosk.domain.vitals import VitalSigns


@dataclass(frozen=True)
class SafetyAlert:
    """Immutable clinical safety contraindication or caution alert.

    Attributes:
        rule_id: Unique safety guideline identifier (e.g. 'RULE-DDI-001').
        severity: Clinical severity level ('CRITICAL_CONTRAINDICATION', 'CAUTION', 'INFO').
        title: Short medical summary of the risk.
        clinical_detail: Detailed pharmacological mechanism and clinical hazard description.
        offending_agents: Tuple of identified interacting or contraindicated medications/allergens.
    """

    rule_id: str
    severity: Literal["CRITICAL_CONTRAINDICATION", "CAUTION", "INFO"]
    title: str
    clinical_detail: str
    offending_agents: tuple[str, ...]


@dataclass(frozen=True)
class PrescriptionSafetyReport:
    """Comprehensive safety clearance report for prescribed medications.

    Attributes:
        is_safe: True if zero CRITICAL_CONTRAINDICATION alerts were triggered.
        severity: Overall risk rating ('SAFE', 'CAUTION', 'CRITICAL_CONTRAINDICATION').
        alerts: Tuple of all identified safety alerts.
    """

    is_safe: bool
    severity: Literal["SAFE", "CAUTION", "CRITICAL_CONTRAINDICATION"]
    alerts: tuple[SafetyAlert, ...]


# Drug Classes and Lexicons
ANTICOAGULANTS = (
    "warfarin",
    "apixaban",
    "rivaroxaban",
    "dabigatran",
    "heparin",
    "enoxaparin",
    "eliquis",
    "xarelto",
    "clexane",
    "acitrom",
)

NSAIDS = (
    "aspirin",
    "ibuprofen",
    "diclofenac",
    "naproxen",
    "ketorolac",
    "indomethacin",
    "aceclofenac",
    "mefenamic",
    "combiflam",
    "voveran",
    "piroxicam",
    "etoricoxib",
    "brufen",
)

NITRATES = (
    "nitroglycerin",
    "isosorbide",
    "sorbitrate",
    "mononitrate",
    "dinitrate",
    "nitrocontin",
    "nitrolingual",
    "isordil",
)

PDE5_INHIBITORS = (
    "sildenafil",
    "tadalafil",
    "vardenafil",
    "viagra",
    "cialis",
    "assurans",
    "penegra",
)

ACE_INHIBITORS_AND_ARBS = (
    "ramipril",
    "enalapril",
    "lisinopril",
    "perindopril",
    "losartan",
    "telmisartan",
    "valsartan",
    "olmesartan",
    "telma",
    "cardace",
    "candelong",
)

K_SPARING_DIURETICS = (
    "spironolactone",
    "eplerenone",
    "aldactone",
    "amiloride",
    "triamterene",
)

BETA_BLOCKERS = (
    "metoprolol",
    "atenolol",
    "propranolol",
    "bisoprolol",
    "carvedilol",
    "labetalol",
    "nebivolol",
    "betaloc",
    "concor",
    "cardivas",
)

PENICILLIN_CROSS_REACTIVE = (
    "amoxicillin",
    "ampicillin",
    "augmentin",
    "amoxiclav",
    "piperacillin",
    "moxikind",
    "penicillin",
    "penidure",
    "clavam",
)

SULFA_CROSS_REACTIVE = (
    "sulfamethoxazole",
    "bactrim",
    "septrin",
    "cotrimoxazole",
    "septran",
    "sulfasalazine",
)

DENGUE_THROMBOCYTOPENIA_PATTERNS = [
    r"\bdengue\b",
    r"\bthrombocytopenia\b",
    r"\bplatelets\s+low\b",
    r"\blow\s+platelet",
    r"\bhaemorrhagic\b",
    r"\bhemorrhagic\b",
    r"\bpetechiae\b",
    r"\bpurpura\b",
    r"\bडेंगू\b",
    r"\bप्लेटलेट\b",
]


def _find_matching_agents(medications: list[str], target_lexicon: tuple[str, ...]) -> list[str]:
    """Identify which medications match any entry in target_lexicon."""
    matched: list[str] = []
    for med in medications:
        med_norm = med.lower()
        for term in target_lexicon:
            if re.search(rf"\b{re.escape(term)}", med_norm):
                matched.append(med)
                break
    return matched


class PharmaSafetyEngine:
    """Pure domain Clinical Decision Support (CDS) engine for prescription safety."""

    @staticmethod
    def _extract_vitals_hemodynamics(
        vitals: VitalSigns | dict[str, Any] | None,
    ) -> tuple[int | None, int | None]:
        """Extract pulse_bpm and systolic_bp_mmhg from vitals."""
        if vitals is None:
            return None, None

        if isinstance(vitals, VitalSigns):
            return vitals.pulse_bpm, vitals.systolic_bp_mmhg

        pulse = vitals.get("pulse_bpm", vitals.get("pulse"))
        sys_bp = vitals.get("systolic_bp_mmhg", vitals.get("systolic_bp", vitals.get("sys_bp")))

        pulse_i = int(pulse) if pulse is not None else None
        sys_i = int(sys_bp) if sys_bp is not None else None
        return pulse_i, sys_i

    @classmethod
    def evaluate(
        cls,
        prescribed_meds: list[str],
        existing_ocr_meds: list[str] | None = None,
        allergies: list[str] | None = None,
        vitals: VitalSigns | dict[str, Any] | None = None,
        symptoms_text: str | list[str] | None = None,
    ) -> PrescriptionSafetyReport:
        """Evaluate medications against DDI, vitals, disease context, and allergies.

        Safety Rules:
        1. Anticoagulant + NSAID -> CRITICAL_CONTRAINDICATION
        2. Nitrate + PDE5i -> CRITICAL_CONTRAINDICATION
        3. Hyperkalemia Duo (ACEi/ARB + K-Sparing Diuretic) -> CAUTION
        4. Beta-Blocker + Bradycardia/Hypotension -> CRITICAL_CONTRAINDICATION
        5. Dengue / Febrile Thrombocytopenia + NSAID -> CRITICAL_CONTRAINDICATION
        6. Drug Allergy Cross-Reaction (Penicillin or Sulfa) -> CRITICAL_CONTRAINDICATION
        """
        all_meds = list(prescribed_meds) + list(existing_ocr_meds or ())
        alerts: list[SafetyAlert] = []

        # Rule 1: Anticoagulant + NSAID
        matched_anticoag = _find_matching_agents(all_meds, ANTICOAGULANTS)
        matched_nsaid = _find_matching_agents(all_meds, NSAIDS)
        # Check if at least one is in prescribed meds
        prescribed_has_anticoag = bool(_find_matching_agents(prescribed_meds, ANTICOAGULANTS))
        prescribed_has_nsaid = bool(_find_matching_agents(prescribed_meds, NSAIDS))

        if (matched_anticoag and matched_nsaid) and (
            prescribed_has_anticoag or prescribed_has_nsaid
        ):
            offenders = tuple(sorted(set(matched_anticoag + matched_nsaid)))
            alerts.append(
                SafetyAlert(
                    rule_id="RULE-DDI-001",
                    severity="CRITICAL_CONTRAINDICATION",
                    title="Severe Hemorrhage Hazard: Anticoagulant + NSAID Co-Prescription",
                    clinical_detail=(
                        "Concurrent administration of oral anticoagulants with NSAIDs drastically "
                        "elevates the hazard of major gastrointestinal and systemic hemorrhage. "
                        "Avoid co-prescription; consider paracetamol or alternative analgesia."
                    ),
                    offending_agents=offenders,
                )
            )

        # Rule 2: Nitrate + PDE5 Inhibitor
        matched_nitrates = _find_matching_agents(all_meds, NITRATES)
        matched_pde5 = _find_matching_agents(all_meds, PDE5_INHIBITORS)
        prescribed_has_nitrate = bool(_find_matching_agents(prescribed_meds, NITRATES))
        prescribed_has_pde5 = bool(_find_matching_agents(prescribed_meds, PDE5_INHIBITORS))

        if (matched_nitrates and matched_pde5) and (prescribed_has_nitrate or prescribed_has_pde5):
            offenders = tuple(sorted(set(matched_nitrates + matched_pde5)))
            alerts.append(
                SafetyAlert(
                    rule_id="RULE-DDI-002",
                    severity="CRITICAL_CONTRAINDICATION",
                    title="Fatal Hypotension Hazard: Nitrate + PDE5 Inhibitor",
                    clinical_detail=(
                        "Combining organic nitrates with phosphodiesterase type 5 (PDE5) "
                        "inhibitors triggers synergistic, potentially refractory vasodilation, "
                        "acute coronary hypoperfusion, and fatal cardiovascular collapse."
                    ),
                    offending_agents=offenders,
                )
            )

        # Rule 3: Hyperkalemia Duo (ACEi/ARB + K-Sparing Diuretic)
        matched_ace_arb = _find_matching_agents(all_meds, ACE_INHIBITORS_AND_ARBS)
        matched_k_sparing = _find_matching_agents(all_meds, K_SPARING_DIURETICS)
        prescribed_has_ace_arb = bool(
            _find_matching_agents(prescribed_meds, ACE_INHIBITORS_AND_ARBS)
        )
        prescribed_has_k_sparing = bool(_find_matching_agents(prescribed_meds, K_SPARING_DIURETICS))

        if (matched_ace_arb and matched_k_sparing) and (
            prescribed_has_ace_arb or prescribed_has_k_sparing
        ):
            offenders = tuple(sorted(set(matched_ace_arb + matched_k_sparing)))
            alerts.append(
                SafetyAlert(
                    rule_id="RULE-DDI-003",
                    severity="CAUTION",
                    title="Hyperkalemia Risk: Renin-Angiotensin Blocker + K-Sparing Diuretic",
                    clinical_detail=(
                        "Dual inhibition of aldosterone action elevates serum potassium levels. "
                        "Concurrent therapy warrants frequent serum electrolyte monitoring "
                        "(serum K+ > 5.5 mEq/L)."
                    ),
                    offending_agents=offenders,
                )
            )

        # Rule 4: Beta-Blocker + Bradycardia / Hypotension
        matched_bb = _find_matching_agents(prescribed_meds, BETA_BLOCKERS)
        pulse_bpm, sys_bp = cls._extract_vitals_hemodynamics(vitals)
        if matched_bb and (pulse_bpm is not None or sys_bp is not None):
            is_bradycardia = pulse_bpm is not None and pulse_bpm < 55
            is_hypotension = sys_bp is not None and sys_bp < 95

            if is_bradycardia or is_hypotension:
                details: list[str] = []
                if is_bradycardia:
                    details.append(f"Heart Rate {pulse_bpm} bpm (< 55 bpm)")
                if is_hypotension:
                    details.append(f"Systolic BP {sys_bp} mmHg (< 95 mmHg)")

                alerts.append(
                    SafetyAlert(
                        rule_id="RULE-VIT-004",
                        severity="CRITICAL_CONTRAINDICATION",
                        title="Cardiogenic Shock / Bradycardia: Beta-Blocker Contraindicated",
                        clinical_detail=(
                            "Beta-blocker prescribed in presence of hemodynamic depression "
                            f"({', '.join(details)}). Risk of acute AV nodal block or "
                            "refractory cardiogenic collapse."
                        ),
                        offending_agents=tuple(sorted(set(matched_bb))),
                    )
                )

        # Rule 5: Dengue / Febrile Thrombocytopenia + NSAID
        matched_nsaid_rx = _find_matching_agents(prescribed_meds, NSAIDS)
        if matched_nsaid_rx:
            if isinstance(symptoms_text, list):
                symptoms_str = " ".join(symptoms_text).lower()
            else:
                symptoms_str = (symptoms_text or "").lower()

            has_dengue_marker = any(
                re.search(pat, symptoms_str) for pat in DENGUE_THROMBOCYTOPENIA_PATTERNS
            )
            if has_dengue_marker:
                alerts.append(
                    SafetyAlert(
                        rule_id="RULE-DIS-005",
                        severity="CRITICAL_CONTRAINDICATION",
                        title="Dengue Hemorrhage Hazard: NSAID Contraindicated",
                        clinical_detail=(
                            "NSAIDs are strictly contraindicated in suspected dengue or "
                            "thrombocytopenic febrile illness due to platelet dysfunction and "
                            "catastrophic gastrointestinal bleeding diathesis. "
                            "Use paracetamol for antipyresis."
                        ),
                        offending_agents=tuple(sorted(set(matched_nsaid_rx))),
                    )
                )

        # Rule 6: Drug Allergy Cross-Reaction Matching
        if allergies:
            allergies_lower = [a.lower() for a in allergies]
            # Penicillin Allergy Check
            has_penicillin_allergy = any(
                "penicillin" in a or "beta-lactam" in a or "penicillins" in a
                for a in allergies_lower
            )
            if has_penicillin_allergy:
                matched_pen = _find_matching_agents(prescribed_meds, PENICILLIN_CROSS_REACTIVE)
                if matched_pen:
                    alerts.append(
                        SafetyAlert(
                            rule_id="RULE-ALG-006",
                            severity="CRITICAL_CONTRAINDICATION",
                            title="Severe Drug Allergy Cross-Reaction: Penicillin / Beta-Lactam",
                            clinical_detail=(
                                "Patient has a declared penicillin / beta-lactam allergy. "
                                f"Prescribed medication ({', '.join(matched_pen)}) presents "
                                "acute anaphylaxis risk."
                            ),
                            offending_agents=tuple(sorted(set(matched_pen))),
                        )
                    )

            # Sulfa Allergy Check
            has_sulfa_allergy = any(
                "sulfa" in a or "sulfonamide" in a or "sulphur" in a for a in allergies_lower
            )
            if has_sulfa_allergy:
                matched_sulfa = _find_matching_agents(prescribed_meds, SULFA_CROSS_REACTIVE)
                if matched_sulfa:
                    alerts.append(
                        SafetyAlert(
                            rule_id="RULE-ALG-007",
                            severity="CRITICAL_CONTRAINDICATION",
                            title="Severe Drug Allergy Cross-Reaction: Sulfonamide",
                            clinical_detail=(
                                "Patient has a declared sulfonamide (sulfa) allergy. "
                                f"Prescribed medication ({', '.join(matched_sulfa)}) presents "
                                "severe hypersensitivity risk."
                            ),
                            offending_agents=tuple(sorted(set(matched_sulfa))),
                        )
                    )

        # Determine overall safety rating
        has_critical = any(a.severity == "CRITICAL_CONTRAINDICATION" for a in alerts)
        has_caution = any(a.severity == "CAUTION" for a in alerts)

        if has_critical:
            overall_severity: Literal["SAFE", "CAUTION", "CRITICAL_CONTRAINDICATION"] = (
                "CRITICAL_CONTRAINDICATION"
            )
            is_safe = False
        elif has_caution:
            overall_severity = "CAUTION"
            is_safe = True
        else:
            overall_severity = "SAFE"
            is_safe = True

        return PrescriptionSafetyReport(
            is_safe=is_safe,
            severity=overall_severity,
            alerts=tuple(alerts),
        )
