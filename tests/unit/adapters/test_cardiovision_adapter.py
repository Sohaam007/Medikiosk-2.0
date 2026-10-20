from medikiosk.adapters.cardiovision import CardioVisionAdapter
from medikiosk.domain.errors import ValidationError


def test_offline_screening_is_deterministic_and_explainable() -> None:
    adapter = CardioVisionAdapter()
    result = adapter.predict({"Age": 72, "HTN": 1, "Typical Chest Pain": 1})

    assert result.meta["mode"] == "mock"
    assert result.cad.prob >= result.vessels["LAD"].prob
    assert result.cad.prob >= result.vessels["LCX"].prob
    assert result.cad.prob >= result.vessels["RCA"].prob
    assert result.explanations["CAD"]
    assert "disclaimer" in result.meta


def test_unknown_feature_is_rejected_at_the_boundary() -> None:
    adapter = CardioVisionAdapter()

    try:
        adapter.predict({"patient_name": "not-a-feature"})
    except ValidationError as exc:
        assert exc.detail == "Unknown cardiovascular screening feature"
    else:
        raise AssertionError("Unknown feature should be rejected")
