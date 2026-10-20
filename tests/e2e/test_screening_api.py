def test_cardiovascular_screening_returns_safe_result(client_kiosk):
    response = client_kiosk.post(
        "/api/screening/cardiovascular",
        json={"features": {"Age": 72, "HTN": 1, "Typical Chest Pain": 1}},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert 0 <= body["cad"]["prob"] <= 1
    assert set(body["vessels"]) == {"LAD", "LCX", "RCA"}
    assert body["meta"]["mode"] == "mock"
    assert "disclaimer" in body["meta"]


def test_cardiovascular_screening_rejects_unknown_feature(client_kiosk):
    response = client_kiosk.post(
        "/api/screening/cardiovascular",
        json={"features": {"patient_name": "should-not-be-accepted"}},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_cardiovascular_referral_returns_non_binding_local_candidates(client_kiosk):
    response = client_kiosk.post(
        "/api/screening/cardiovascular/referral",
        json={
            "features": {"Age": 72, "HTN": 1, "Typical Chest Pain": 1},
            "preferred_language": "hi-IN",
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    recommendation = body["recommendation"]
    assert recommendation["reason_code"] == "CARDIO_SCREEN_REVIEW"
    assert recommendation["priority"] == "urgent"
    assert recommendation["requires_clinician_review"] is True
    assert recommendation["doctor_ids"]
    assert recommendation["package_ids"]
    assert "disclaimer" in body["screening"]["meta"]


def test_low_risk_referral_does_not_force_cardiology(client_kiosk):
    response = client_kiosk.post(
        "/api/screening/cardiovascular/referral",
        json={"features": {"Age": 30, "HTN": 0, "DM": 0, "Typical Chest Pain": 0}},
    )

    assert response.status_code == 200, response.text
    recommendation = response.json()["recommendation"]
    assert recommendation["reason_code"] == "NO_AUTOMATIC_REFERRAL"
    assert recommendation["doctor_ids"] == []
    assert recommendation["package_ids"] == []
