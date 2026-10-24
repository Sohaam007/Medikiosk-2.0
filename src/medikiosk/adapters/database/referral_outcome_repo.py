"""SQLAlchemy repository for local referral workflow outcomes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from medikiosk.adapters.database.models import ReferralOutcomeModel
from medikiosk.domain.contracts import ReferralCandidateType, ReferralOutcome, ReferralOutcomeStatus
from medikiosk.domain.errors import (
    ReferralOutcomeConflictError,
    ReferralOutcomeNotFoundError,
    StorageError,
)


class SQLReferralOutcomeRepository:
    """SQLAlchemy-backed current-state repository for referral outcomes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_model(outcome: ReferralOutcome) -> ReferralOutcomeModel:
        return ReferralOutcomeModel(
            outcome_id=str(outcome.outcome_id),
            session_id=str(outcome.session_id),
            candidate_id=str(outcome.candidate_id),
            candidate_type=outcome.candidate_type.value,
            status=outcome.status.value,
            created_at=outcome.created_at,
            updated_at=outcome.updated_at,
        )

    @staticmethod
    def _to_domain(model: ReferralOutcomeModel) -> ReferralOutcome:
        def with_utc(value: datetime) -> datetime:
            return value if value.tzinfo is not None else value.replace(tzinfo=UTC)

        return ReferralOutcome(
            outcome_id=UUID(model.outcome_id),
            session_id=UUID(model.session_id),
            candidate_id=UUID(model.candidate_id),
            candidate_type=ReferralCandidateType(model.candidate_type),
            status=ReferralOutcomeStatus(model.status),
            created_at=with_utc(model.created_at),
            updated_at=with_utc(model.updated_at),
        )

    async def create(self, outcome: ReferralOutcome) -> ReferralOutcome:
        try:
            self._session.add(self._to_model(outcome))
            await self._session.flush()
            return outcome
        except IntegrityError as exc:
            raise ReferralOutcomeConflictError(
                "Referral candidate already has a workflow outcome for this session"
            ) from exc
        except SQLAlchemyError as exc:
            raise StorageError(f"Failed to create referral outcome: {type(exc).__name__}") from exc

    async def get(self, outcome_id: UUID) -> ReferralOutcome | None:
        try:
            result = await self._session.execute(
                select(ReferralOutcomeModel).where(
                    ReferralOutcomeModel.outcome_id == str(outcome_id)
                )
            )
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model is not None else None
        except SQLAlchemyError as exc:
            raise StorageError(f"Failed to fetch referral outcome: {type(exc).__name__}") from exc

    async def update(self, outcome: ReferralOutcome) -> ReferralOutcome:
        try:
            result = await self._session.execute(
                select(ReferralOutcomeModel).where(
                    ReferralOutcomeModel.outcome_id == str(outcome.outcome_id)
                )
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ReferralOutcomeNotFoundError("Referral outcome not found")
            model.status = outcome.status.value
            model.updated_at = outcome.updated_at
            await self._session.flush()
            return outcome
        except ReferralOutcomeNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise StorageError(f"Failed to update referral outcome: {type(exc).__name__}") from exc

    async def get_for_candidate(
        self,
        session_id: UUID,
        candidate_type: ReferralCandidateType,
        candidate_id: UUID,
    ) -> ReferralOutcome | None:
        try:
            result = await self._session.execute(
                select(ReferralOutcomeModel).where(
                    ReferralOutcomeModel.session_id == str(session_id),
                    ReferralOutcomeModel.candidate_type == candidate_type.value,
                    ReferralOutcomeModel.candidate_id == str(candidate_id),
                )
            )
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model is not None else None
        except SQLAlchemyError as exc:
            raise StorageError(
                f"Failed to fetch referral candidate outcome: {type(exc).__name__}"
            ) from exc

    async def list_for_session(self, session_id: UUID) -> list[ReferralOutcome]:
        try:
            result = await self._session.execute(
                select(ReferralOutcomeModel)
                .where(ReferralOutcomeModel.session_id == str(session_id))
                .order_by(ReferralOutcomeModel.created_at, ReferralOutcomeModel.outcome_id)
            )
            return [self._to_domain(model) for model in result.scalars().all()]
        except SQLAlchemyError as exc:
            raise StorageError(f"Failed to list referral outcomes: {type(exc).__name__}") from exc
