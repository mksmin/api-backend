from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions import ProjectNotFoundError
from app_exceptions import UserNotFoundError
from core.crud.dependencies import validate_uuid_str
from core.crud.managers import ProjectManager
from core.crud.managers import UserManager
from core.crud.managers.lms_flows import LMSFlowManager
from schemas.lms_flows import LMSFlowsCreateModel
from schemas.lms_flows import LMSFlowsCreateSchema
from schemas.lms_flows import LMSFlowsReadSchema

FLOW_TITLE_UNIQUE_INDEX = "uq_lms_flows_project_id_title_active"


class FlowNotFoundError(Exception): ...


class FlowAlreadyExistsError(Exception): ...


class LMSFlowsService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.manager = LMSFlowManager(session)
        self.user_manager = UserManager(session)
        self.project_manager = ProjectManager(session)

    async def _require_project_access(
        self,
        project_id: int,
        user_id: int,
    ) -> None:
        user = await self.user_manager.get_by_id(user_id)
        if user is None or user.deleted_at is not None:
            raise UserNotFoundError

        project = await self.project_manager.get_by_id(project_id)
        if project is None or project.owner_id != user_id:
            raise ProjectNotFoundError

    @staticmethod
    def _validate_uuid(
        uuid: UUID | str,
    ) -> UUID:
        if isinstance(uuid, UUID):
            return uuid

        return validate_uuid_str(uuid)

    @asynccontextmanager
    async def _write(self) -> AsyncIterator[None]:
        committed = False

        try:
            yield
            await self.session.commit()
            committed = True
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint_name = getattr(cause, "constraint_name", None)

            if constraint_name == FLOW_TITLE_UNIQUE_INDEX:
                raise FlowAlreadyExistsError from exc

            raise
        finally:
            if not committed:
                await self.session.rollback()

    async def get_all(
        self,
        project_id: int,
        *,
        user_id: int,
    ) -> list[LMSFlowsReadSchema]:
        await self._require_project_access(
            project_id=project_id,
            user_id=user_id,
        )

        flows = await self.manager.get_all(
            project_id=project_id,
        )
        return [LMSFlowsReadSchema.model_validate(flow) for flow in flows]

    async def get_by_uuid(
        self,
        project_id: int,
        flow_uuid: UUID | str,
        *,
        user_id: int,
    ) -> LMSFlowsReadSchema:
        await self._require_project_access(
            project_id=project_id,
            user_id=user_id,
        )

        flow = await self.manager.get_by_uuid(
            project_id=project_id,
            flow_uuid=self._validate_uuid(flow_uuid),
        )
        if flow is None:
            raise FlowNotFoundError

        return LMSFlowsReadSchema.model_validate(flow)

    async def create_flow(
        self,
        project_id: int,
        flow_in: LMSFlowsCreateSchema,
        *,
        user_id: int,
    ) -> LMSFlowsReadSchema:
        async with self._write():
            await self._require_project_access(
                project_id=project_id,
                user_id=user_id,
            )

            flow = await self.manager.create(
                LMSFlowsCreateModel(
                    title=flow_in.title,
                    project_id=project_id,
                ),
            )

            await self.session.flush()
            return LMSFlowsReadSchema.model_validate(flow)
