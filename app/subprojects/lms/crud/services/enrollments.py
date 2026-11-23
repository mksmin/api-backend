from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions import ProjectNotFoundError
from app_exceptions import UserNotFoundError
from app_exceptions.exceptions import EnrollmentAlreadyExistsError
from app_exceptions.exceptions import EnrollmentRestoreRequiredError
from app_exceptions.exceptions import ParticipantCreationConflictError
from app_exceptions.exceptions import ParticipantUnavailableError
from core.crud.managers import UserManager
from core.database import Project
from schemas.lms.enrollments import LMSEnrollmentsCreateModel
from schemas.lms.enrollments import LMSEnrollmentsCreateSchema
from schemas.lms.enrollments import LMSEnrollmentsReadSchema
from schemas.lms.participants import LMSParticipantsCreateSchema
from subprojects.lms.crud.managers import LMSFlowManager
from subprojects.lms.crud.managers import ProjectManager
from subprojects.lms.crud.managers.enrollments import LMSEnrollmentsManager
from subprojects.lms.crud.managers.participants import LMSParticipantsManager
from subprojects.lms.crud.services.lms_flows import FlowNotFoundError


class LMSEnrollmentsService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.manager: LMSEnrollmentsManager = LMSEnrollmentsManager(session)
        self.participants_manager: LMSParticipantsManager = LMSParticipantsManager(
            session,
        )
        self.flow_manager: LMSFlowManager = LMSFlowManager(session)
        self.project_manager: ProjectManager = ProjectManager(session)
        self.user_manager: UserManager = UserManager(session)

    async def _require_project_access(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        user = await self.user_manager.get_by_id(user_id)
        if user is None or user.deleted_at is not None:
            raise UserNotFoundError

        project = await self.project_manager.get_by_id(project_id)
        if project is None or project.owner_id != user_id:
            raise ProjectNotFoundError

        return project

    @asynccontextmanager
    async def _write(self) -> AsyncIterator[None]:
        committed = False

        try:
            yield
            await self.session.commit()
            committed = True

        except IntegrityError as exc:
            cause = getattr(
                exc.orig,
                "__cause__",
                None,
            )
            constraint_name = getattr(
                cause,
                "constraint_name",
                None,
            )

            if constraint_name == "uq_lms_enrollments_project_participant":
                raise EnrollmentAlreadyExistsError from exc

            if constraint_name == "uq_lms_participant_email_lower":
                raise ParticipantCreationConflictError from exc

            raise
        finally:
            if not committed:
                await self.session.rollback()

    async def create_enrollment(
        self,
        project_id: int,
        enrollment_in: LMSEnrollmentsCreateSchema,
        *,
        user_id: int,
    ) -> LMSEnrollmentsReadSchema:
        async with self._write():
            project = await self._require_project_access(
                project_id=project_id,
                user_id=user_id,
            )

            flow = await self.flow_manager.get_by_uuid(
                project_id=project_id,
                flow_uuid=enrollment_in.flow_uuid,
            )
            if flow is None:
                raise FlowNotFoundError

            participant = await self.participants_manager.get_by_email(
                email=enrollment_in.email,
            )

            if participant is None:
                participant = await self.participants_manager.create(
                    LMSParticipantsCreateSchema(
                        full_name=enrollment_in.full_name,
                        email=enrollment_in.email,
                    ),
                )
                await self.session.flush()
            elif participant.deleted_at is not None:
                raise ParticipantUnavailableError

            existing = await self.manager.get_by_participant(
                project_id=project_id,
                participant_id=participant.id,
            )

            if existing is not None:
                if existing.status == "excluded":
                    raise EnrollmentRestoreRequiredError
                raise EnrollmentAlreadyExistsError

            enrollment = await self.manager.create(
                LMSEnrollmentsCreateModel(
                    project_id=project_id,
                    participant_id=participant.id,
                    flow_id=flow.id,
                ),
            )
            await self.session.flush()

            return LMSEnrollmentsReadSchema(
                id=enrollment.id,
                uuid=enrollment.uuid,
                project_uuid=project.uuid,
                participant_uuid=participant.uuid,
                full_name=participant.full_name,
                email=participant.email,
                flow_uuid=flow.uuid,
                flow_title=flow.title,
                status=enrollment.status,
                created_at=enrollment.created_at,
            )

    async def get_all(
        self,
        project_id: int,
        *,
        user_id: int,
        flow_uuid: UUID | None = None,
        active_only: bool = False,
    ) -> list[LMSEnrollmentsReadSchema]:
        await self._require_project_access(
            project_id=project_id,
            user_id=user_id,
        )

        rows = await self.manager.get_all(
            project_id=project_id,
            flow_uuid=flow_uuid,
            active_only=active_only,
        )

        return [LMSEnrollmentsReadSchema.model_validate(row) for row in rows]

    async def count_by_project(
        self,
        project_id: int,
        *,
        user_id: int,
    ) -> int:
        await self._require_project_access(
            project_id=project_id,
            user_id=user_id,
        )
        return await self.manager.count_by_project(project_id=project_id)

    async def count_by_owned_projects(
        self,
        *,
        user_id: int,
    ) -> dict[UUID, int]:
        user = await self.user_manager.get_by_id(user_id)
        if user is None or user.deleted_at is not None:
            raise UserNotFoundError

        return await self.manager.count_by_owned_projects(owner_id=user_id)
