from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import RowMapping
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import LMSFlow
from core.database import Project
from core.database.lms import LMSEnrollment
from core.database.lms import LMSParticipant
from schemas.lms.enrollments import LMSEnrollmentsCreateModel


class LMSEnrollmentsManager:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_by_participant(
        self,
        project_id: int,
        participant_id: int,
    ) -> LMSEnrollment | None:
        stmt = select(
            LMSEnrollment,
        ).where(
            LMSEnrollment.project_id == project_id,
            LMSEnrollment.participant_id == participant_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        enrolment_in: LMSEnrollmentsCreateModel,
    ) -> LMSEnrollment:
        enrollment = LMSEnrollment(
            **enrolment_in.model_dump(),
        )
        self.session.add(enrollment)
        return enrollment

    async def get_all(
        self,
        project_id: int,
        *,
        flow_uuid: UUID | None = None,
        active_only: bool = False,
    ) -> Sequence[RowMapping]:
        stmt = (
            select(
                LMSEnrollment.id,
                LMSEnrollment.uuid,
                Project.uuid.label("project_uuid"),
                LMSParticipant.uuid.label("participant_uuid"),
                LMSParticipant.full_name,
                LMSParticipant.email,
                LMSFlow.uuid.label("flow_uuid"),
                LMSFlow.title.label("flow_title"),
                LMSEnrollment.status,
                LMSEnrollment.created_at,
            )
            .select_from(LMSEnrollment)
            .join(
                Project,
                Project.id == LMSEnrollment.project_id,
            )
            .join(
                LMSParticipant,
                LMSParticipant.id == LMSEnrollment.participant_id,
            )
            .join(
                LMSFlow,
                LMSFlow.id == LMSEnrollment.flow_id,
            )
            .where(
                LMSEnrollment.project_id == project_id,
                LMSEnrollment.deleted_at.is_(None),
                LMSParticipant.deleted_at.is_(None),
                Project.deleted_at.is_(None),
            )
            .order_by(
                LMSParticipant.full_name,
                LMSEnrollment.id,
            )
        )

        if flow_uuid is not None:
            stmt = stmt.where(LMSFlow.uuid == flow_uuid)
        if active_only:
            stmt = stmt.where(LMSEnrollment.status == "active")

        result = await self.session.execute(stmt)
        return result.mappings().all()

    async def count_by_project(
        self,
        project_id: int,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(LMSEnrollment)
            .join(
                LMSParticipant,
                LMSParticipant.id == LMSEnrollment.participant_id,
            )
            .where(
                LMSEnrollment.project_id == project_id,
                LMSEnrollment.status == "active",
                LMSEnrollment.deleted_at.is_(None),
                LMSParticipant.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_by_owned_projects(
        self,
        owner_id: int,
    ) -> dict[UUID, int]:
        stmt = (
            select(
                Project.uuid,
                func.count(LMSEnrollment.id),
            )
            .select_from(Project)
            .join(
                LMSEnrollment,
                LMSEnrollment.project_id == Project.id,
            )
            .join(
                LMSParticipant,
                LMSParticipant.id == LMSEnrollment.participant_id,
            )
            .where(
                Project.owner_id == owner_id,
                Project.deleted_at.is_(None),
                LMSEnrollment.status == "active",
                LMSEnrollment.deleted_at.is_(None),
                LMSParticipant.deleted_at.is_(None),
            )
            .group_by(Project.uuid)
        )
        result = await self.session.execute(stmt)
        return dict(
            result.all(),
        )
