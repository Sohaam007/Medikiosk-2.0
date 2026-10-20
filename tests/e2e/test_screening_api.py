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
