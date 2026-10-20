"""Unit tests for Clinical Standing Orders (CSO) & Pre-Consultation Lab Router engine.

Zero I/O, zero network, zero logging. Pure deterministic unit testing.
"""

from __future__ import annotations

import pytest

from medikiosk.domain.standing_orders import (
    ORDER_ABG,
    ORDER_CAPILLARY_BG,
    ORDER_CBC_PLATELETS,
    ORDER_DENGUE_RAPID,
    ORDER_DIGITAL_CXR,
    ORDER_MALARIA_RAPID,
    ORDER_POC_TROPONIN,
    ORDER_STAT_ECG,
    StandingOrdersEngine,
)
from medikiosk.domain.vitals import VitalSigns


@pytest.fixture
def normal_vitals() -> VitalSigns:
    return VitalSigns(
        spo2_percent=98,
        systolic_bp_mmhg=120,
        diastolic_bp_mmhg=80,
        pulse_bpm=72,
        temperature_c=36.8,
        respiration_rate=16,
    )


def test_cardiac_symptoms_trigger_ecg_and_troponin(normal_vitals: VitalSigns) -> None:
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Severe chest pain radiating to the left arm and jaw",
        age=35,
        vitals=normal_vitals,
    )
    assert ORDER_STAT_ECG in rec.orders
    assert ORDER_POC_TROPONIN in rec.orders
    assert rec.estimated_time_saved_minutes == 45
    assert "acute coronary syndrome" in rec.clinical_rationale.lower()
    assert rec.requires_fasting is False


def test_cardiac_hindi_keywords(normal_vitals: VitalSigns) -> None:
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Bahut tez seene mein dard hai aur paseena aa raha hai",
        age=40,
        vitals=normal_vitals,
    )
    assert ORDER_STAT_ECG in rec.orders
    assert ORDER_POC_TROPONIN in rec.orders
    assert any(o.code == "ECG-01" for o in rec.orders)
    assert any(o.code == "LAB-TROP" for o in rec.orders)


def test_red_triage_triggers_cardiac(normal_vitals: VitalSigns) -> None:
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="chest discomfort",
        age=42,
        vitals=normal_vitals,
        triage_priority="RED",
    )
    assert ORDER_STAT_ECG in rec.orders
    assert ORDER_POC_TROPONIN in rec.orders


def test_acute_fever_temp_trigger() -> None:
    fever_vitals = VitalSigns(
        spo2_percent=97,
        systolic_bp_mmhg=118,
        diastolic_bp_mmhg=78,
        pulse_bpm=95,
        temperature_c=38.6,
        respiration_rate=18,
    )
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Mild weakness",
        age=30,
        vitals=fever_vitals,
    )
    assert ORDER_CBC_PLATELETS in rec.orders
    assert ORDER_DENGUE_RAPID in rec.orders
    assert ORDER_MALARIA_RAPID in rec.orders
    assert rec.estimated_time_saved_minutes == 60
    assert "Phlebotomy Bay 2" in [o.bay_room for o in rec.orders]


def test_acute_fever_symptoms_keywords(normal_vitals: VitalSigns) -> None:
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="3 din se tez bukhar aur chills ho rahe hain",
        age=28,
        vitals=normal_vitals,
    )
    assert ORDER_CBC_PLATELETS in rec.orders
    assert ORDER_DENGUE_RAPID in rec.orders
    assert ORDER_MALARIA_RAPID in rec.orders
    assert rec.estimated_time_saved_minutes == 60


def test_respiratory_hypoxia_spo2_trigger() -> None:
    hypoxic_vitals = VitalSigns(
        spo2_percent=92,
        systolic_bp_mmhg=125,
        diastolic_bp_mmhg=82,
        pulse_bpm=100,
        temperature_c=36.9,
        respiration_rate=20,
    )
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Feeling tired",
        age=35,
        vitals=hypoxic_vitals,
    )
    assert ORDER_DIGITAL_CXR in rec.orders
    assert ORDER_ABG in rec.orders
    assert rec.estimated_time_saved_minutes == 40
    assert "Radiology Room 105" in [o.bay_room for o in rec.orders]
    assert "Phlebotomy Bay 1" in [o.bay_room for o in rec.orders]


def test_respiratory_symptoms_keywords(normal_vitals: VitalSigns) -> None:
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Shortness of breath and saans lene mein dikkat",
        age=38,
        vitals=normal_vitals,
    )
    assert ORDER_DIGITAL_CXR in rec.orders
    assert ORDER_ABG in rec.orders
    assert rec.estimated_time_saved_minutes == 40


def test_respiratory_tachypnea_trigger() -> None:
    tachypneic_vitals = VitalSigns(
        spo2_percent=96,
        systolic_bp_mmhg=122,
        diastolic_bp_mmhg=80,
        pulse_bpm=88,
        temperature_c=36.7,
        respiration_rate=24,
    )
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="",
        age=32,
        vitals=tachypneic_vitals,
    )
    assert ORDER_DIGITAL_CXR in rec.orders
    assert ORDER_ABG in rec.orders


def test_metabolic_screening_age_45(normal_vitals: VitalSigns) -> None:
    rec_under_45 = StandingOrdersEngine.evaluate(
        symptoms_text="Routine checkup",
        age=44,
        vitals=normal_vitals,
    )
    assert ORDER_CAPILLARY_BG not in rec_under_45.orders

    rec_45_plus = StandingOrdersEngine.evaluate(
        symptoms_text="Routine checkup",
        age=45,
        vitals=normal_vitals,
    )
    assert ORDER_CAPILLARY_BG in rec_45_plus.orders
    assert rec_45_plus.estimated_time_saved_minutes == 15


def test_multi_rule_co_occurrence_and_deduplication() -> None:
    vitals = VitalSigns(
        spo2_percent=93,
        systolic_bp_mmhg=130,
        diastolic_bp_mmhg=85,
        pulse_bpm=102,
        temperature_c=38.8,
        respiration_rate=23,
    )
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Severe chest pain and high fever with chills",
        age=52,
        vitals=vitals,
    )
    # Cardiac (45) + Fever (60) + Respiratory (40) + Metabolic (15) = 160 minutes
    assert rec.estimated_time_saved_minutes == 160
    codes = [o.code for o in rec.orders]
    assert len(codes) == len(set(codes)), "Orders must be uniquely deduplicated"
    assert "ECG-01" in codes
    assert "LAB-TROP" in codes
    assert "LAB-CBC" in codes
    assert "LAB-DENGUE" in codes
    assert "LAB-MP" in codes
    assert "RAD-CXR" in codes
    assert "LAB-ABG" in codes
    assert "LAB-CBG" in codes


def test_benign_symptoms_no_orders(normal_vitals: VitalSigns) -> None:
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="Mild ear itching since yesterday",
        age=24,
        vitals=normal_vitals,
    )
    assert len(rec.orders) == 0
    assert rec.estimated_time_saved_minutes == 0
    assert "No standing pre-consultation orders" in rec.clinical_rationale


def test_vitals_as_dict() -> None:
    vitals_dict = {
        "temperature_c": 39.2,
        "spo2_percent": 90,
        "respiration_rate": 20,
    }
    rec = StandingOrdersEngine.evaluate(
        symptoms_text="",
        age=30,
        vitals=vitals_dict,
    )
    assert ORDER_CBC_PLATELETS in rec.orders
    assert ORDER_DIGITAL_CXR in rec.orders
    assert rec.estimated_time_saved_minutes == 100  # 60 + 40
