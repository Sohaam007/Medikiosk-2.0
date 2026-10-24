from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio

from medikiosk.adapters.database.engine import create_all_tables, get_engine, get_session_factory
from medikiosk.adapters.database.referral_outcome_repo import SQLReferralOutcomeRepository
from medikiosk.adapters.database.session_repo import SQLSessionRepository
from medikiosk.domain.contracts import (
    InformantType,
    ReferralCandidateType,
    ReferralOutcome,
    ReferralOutcomeStatus,
    SessionState,
    SessionStatus,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
NOW = datetime(2026, 10, 25, 12, 0, tzinfo=UTC)


@pytest_asyncio.fixture
async def db_session_factory():
    get_engine.cache_clear()
    engine = get_engine(TEST_DB_URL)
    await create_all_tables(engine)
    factory = get_session_factory(engine)
    yield factory
    await engine.dispose()
    get_engine.cache_clear()


@pytest.mark.asyncio
async def test_sqlite_referral_outcome_table_creates_reads_and_updates(db_session_factory) -> None:
    session_id = uuid4()
    async with db_session_factory() as db:
        session_repo = SQLSessionRepository(db)
        outcome_repo = SQLReferralOutcomeRepository(db)
        await session_repo.create(
            SessionState(
                session_id=session_id,
                patient_language="en",
                created_at=NOW,
                status=SessionStatus.ACTIVE,
                consent_status=True,
                intake_progress=1.0,
                informant_type=InformantType.PATIENT,
            )
        )
        outcome = ReferralOutcome(
            outcome_id=uuid4(),
            session_id=session_id,
            candidate_id=uuid4(),
            candidate_type=ReferralCandidateType.PACKAGE,
            status=ReferralOutcomeStatus.RECOMMENDED,
            created_at=NOW,
            updated_at=NOW,
        )

        await outcome_repo.create(outcome)
        stored = await outcome_repo.get(outcome.outcome_id)
        assert stored == outcome

        updated = outcome.model_copy(
            update={
                "status": ReferralOutcomeStatus.REVIEWED,
                "updated_at": NOW,
            }
        )
        await outcome_repo.update(updated)
        assert await outcome_repo.list_for_session(session_id) == [updated]
