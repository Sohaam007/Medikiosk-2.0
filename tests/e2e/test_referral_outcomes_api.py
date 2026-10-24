from datetime import UTC, datetime
from uuid import uuid4

import pytest

from medikiosk.api.app import create_app
from medikiosk.api.dependencies.auth import require_clinician
from medikiosk.api.dependencies.container import get_referral_outcome_service_dep
from medikiosk.domain.contracts import (
    InformantType,
    SessionState,
    SessionStatus,
)
from medikiosk.services.referral_outcome_service import ReferralOutcomeService
from tests.e2e.conftest import (
    FakeAuditRepo,
    FakeOutcomeRepository,
    FakeSessionRepo,
    get_fake_kiosk_user,
    get_fake_nurse_user,
)

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=UTC)


@pytest.fixture
def referral_api_client():
    session_repo = FakeSessionRepo()
    audit_repo = FakeAuditRepo()
    outcome_repo = FakeOutcomeRepository()
    service = ReferralOutcomeService(outcome_repo, session_repo, audit_repo)
    app = create_app()
    app.dependency_overrides[get_referral_outcome_service_dep] = lambda: service
    app.dependency_overrides[require_clinician] = get_fake_nurse_user
    session_id = uuid4()
    session_repo._store[str(session_id)] = SessionState(
        session_id=session_id,
        patient_language="en",
        created_at=NOW,
        status=SessionStatus.ACTIVE,
        consent_status=True,
        intake_progress=1.0,
        informant_type=InformantType.PATIENT,
    )
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client, session_id


def test_clinician_can_create_transition_and_read_referral_outcome(referral_api_client) -> None:
    client, session_id = referral_api_client
    candidate_id = uuid4()
    create_response = client.post(
        "/api/clinician/referral-outcomes",
        json={
            "session_id": str(session_id),
            "candidate_id": str(candidate_id),
            "candidate_type": "doctor",
        },
    )
    assert create_response.status_code == 201, create_response.text
    outcome_id = create_response.json()["outcome_id"]

    transition_response = client.post(
        f"/api/clinician/referral-outcomes/{outcome_id}/transition",
        json={"status": "reviewed"},
    )
    assert transition_response.status_code == 200, transition_response.text
    assert transition_response.json()["status"] == "reviewed"

    list_response = client.get(
        "/api/clinician/referral-outcomes",
        params={"session_id": str(session_id)},
    )
    assert list_response.status_code == 200
    assert list_response.json()["total_count"] == 1
    assert list_response.json()["items"][0]["candidate_id"] == str(candidate_id)


def test_kiosk_role_is_rejected_for_referral_writes(referral_api_client) -> None:
    client, session_id = referral_api_client
    client.app.dependency_overrides[require_clinician] = get_fake_kiosk_user

    response = client.post(
        "/api/clinician/referral-outcomes",
        json={
            "session_id": str(session_id),
            "candidate_id": str(uuid4()),
            "candidate_type": "doctor",
        },
    )

    assert response.status_code == 403
