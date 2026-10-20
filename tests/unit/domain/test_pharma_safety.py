"""Unit tests for Pharmacovigilance Drug-Drug Interaction (DDI) & Safety Firewall Engine.

Zero I/O, zero network, zero logging. Pure deterministic unit testing.
"""

from __future__ import annotations

from medikiosk.domain.pharma_safety import PharmaSafetyEngine
from medikiosk.domain.vitals import VitalSigns


def test_rule1_anticoagulant_and_nsaid_critical_contraindication() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Warfarin Sodium 5mg", "Tab Aspirin 75mg"],
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-DDI-001" for a in rep.alerts)
    alert = next(a for a in rep.alerts if a.rule_id == "RULE-DDI-001")
    assert alert.severity == "CRITICAL_CONTRAINDICATION"
    assert "Warfarin Sodium 5mg" in alert.offending_agents
    assert "Tab Aspirin 75mg" in alert.offending_agents


def test_rule1_ocr_anticoagulant_with_prescribed_nsaid() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Tab Combiflam (Ibuprofen + Paracetamol)"],
        existing_ocr_meds=["Eliquis (Apixaban) 5mg"],
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-DDI-001" for a in rep.alerts)


def test_rule2_nitrate_and_pde5i_critical_contraindication() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Sorbitrate (Isosorbide Dinitrate) 10mg", "Sildenafil 50mg"],
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-DDI-002" for a in rep.alerts)
    alert = next(a for a in rep.alerts if a.rule_id == "RULE-DDI-002")
    assert "Fatal Hypotension" in alert.title


def test_rule2_ocr_nitrate_with_prescribed_pde5i() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Tadalafil 20mg"],
        existing_ocr_meds=["Nitroglycerin sublingual spray"],
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-DDI-002" for a in rep.alerts)


def test_rule3_hyperkalemia_duo_caution() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Ramipril 5mg", "Spironolactone 25mg"],
    )
    assert rep.is_safe is True
    assert rep.severity == "CAUTION"
    assert any(a.rule_id == "RULE-DDI-003" for a in rep.alerts)
    alert = next(a for a in rep.alerts if a.rule_id == "RULE-DDI-003")
    assert alert.severity == "CAUTION"


def test_rule3_arb_and_aldactone() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Telmisartan 40mg"],
        existing_ocr_meds=["Tab Aldactone 50mg"],
    )
    assert rep.is_safe is True
    assert rep.severity == "CAUTION"
    assert any(a.rule_id == "RULE-DDI-003" for a in rep.alerts)


def test_rule4_beta_blocker_with_bradycardia() -> None:
    brady_vitals = VitalSigns(
        spo2_percent=98,
        systolic_bp_mmhg=110,
        diastolic_bp_mmhg=70,
        pulse_bpm=46,  # < 55 bpm
        temperature_c=36.7,
        respiration_rate=16,
    )
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Metoprolol Tartrate 50mg"],
        vitals=brady_vitals,
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-VIT-004" for a in rep.alerts)


def test_rule4_beta_blocker_with_hypotension() -> None:
    hypotensive_vitals = {
        "pulse_bpm": 70,
        "systolic_bp_mmhg": 88,  # < 95 mmHg
    }
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Atenolol 25mg"],
        vitals=hypotensive_vitals,
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-VIT-004" for a in rep.alerts)


def test_rule4_beta_blocker_with_normal_vitals_safe() -> None:
    normal_vitals = VitalSigns(
        spo2_percent=98,
        systolic_bp_mmhg=125,
        diastolic_bp_mmhg=80,
        pulse_bpm=75,
        temperature_c=36.8,
        respiration_rate=16,
    )
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Bisoprolol 5mg"],
        vitals=normal_vitals,
    )
    assert rep.is_safe is True
    assert rep.severity == "SAFE"
    assert len(rep.alerts) == 0


def test_rule5_dengue_syndrome_nsaid_contraindication() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Voveran (Diclofenac) 50mg"],
        symptoms_text="Severe joint pain and diagnosed with dengue fever",
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-DIS-005" for a in rep.alerts)


def test_rule5_thrombocytopenia_nsaid_contraindication() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Brufen 400mg"],
        symptoms_text="Patient has severe thrombocytopenia with low platelets count",
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-DIS-005" for a in rep.alerts)


def test_rule6_penicillin_allergy_cross_reaction() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Augmentin 625mg Duo"],
        allergies=["Severe Penicillin Allergy (Rash & Wheezing)"],
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-ALG-006" for a in rep.alerts)


def test_rule6_sulfa_allergy_cross_reaction() -> None:
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Tab Bactrim DS (Sulfamethoxazole + Trimethoprim)"],
        allergies=["Sulfa drugs"],
    )
    assert rep.is_safe is False
    assert rep.severity == "CRITICAL_CONTRAINDICATION"
    assert any(a.rule_id == "RULE-ALG-007" for a in rep.alerts)


def test_clean_prescription_completely_safe() -> None:
    normal_vitals = VitalSigns(
        spo2_percent=99,
        systolic_bp_mmhg=118,
        diastolic_bp_mmhg=76,
        pulse_bpm=68,
        temperature_c=36.6,
        respiration_rate=14,
    )
    rep = PharmaSafetyEngine.evaluate(
        prescribed_meds=["Paracetamol 650mg", "Pantoprazole 40mg", "Cetirizine 10mg"],
        existing_ocr_meds=["Multivitamin syrup"],
        allergies=["Dust mites"],
        vitals=normal_vitals,
        symptoms_text="Seasonal allergies and mild headache",
    )
    assert rep.is_safe is True
    assert rep.severity == "SAFE"
    assert len(rep.alerts) == 0
