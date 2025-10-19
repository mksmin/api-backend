from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app_exceptions import (
    InvalidUUIDError,
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    UserNotFoundError,
)
from core.crud.managers import ProjectManager, UserManager
from schemas import (
    ProjectCreateModel,
    ProjectCreateSchema,
    ProjectReadSchema,
    ProjectSchema,
)


def validate_uuid_str(
    project_uuid: str,
) -> UUID:
    try:
        return UUID(project_uuid)
    except ValueError as e:
        raise InvalidUUIDError from e


class ProjectService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.manager = ProjectManager(self.session)
        self.user_manager = UserManager(self.session)

    async def create_project(
        self,
        project_create: ProjectCreateSchema,
        user_id: int,
    ) -> ProjectReadSchema:
        user = await self.user_manager.get_by_id(user_id)
        if not user:
            raise UserNotFoundError

        project_data = project_create.model_dump()
        if await self.manager.get_project_by_field(
            owner_id=user.id,
            field="title",
            value=project_data["title"],
        ):
            raise ProjectAlreadyExistsError

        project_create_model = ProjectCreateModel(
            **project_data,
            owner_id=user.id,
        )

        project = await self.manager.create(project_create_model)

        await self.session.commit()

        return ProjectReadSchema.model_validate(
            project,
            context={"owner_uuid": user.uuid},
        )

    async def get_by_uuid(
        self,
        user_id: int,
        project_uuid: str,
    ) -> ProjectSchema:
        project_uuid = validate_uuid_str(project_uuid)
        user = await self.user_manager.get_by_id(user_id)
        if not user:
            raise UserNotFoundError

        project = await self.manager.get_by_uuid(project_uuid)
        try:
            return ProjectSchema.model_validate(
                project,
                context={
                    "owner_uuid": user.uuid,
                },
            )
        except ValidationError as e:
            raise ProjectNotFoundError from e

    async def get_all(
        self,
        user_id: int,
    ) -> list[ProjectReadSchema]:
        user = await self.user_manager.get_by_id(user_id)
        if not user:
            raise UserNotFoundError

        projects = await self.manager.get_all(user_id=user.id)

        return [
            ProjectReadSchema.model_validate(
                projects,
                context={"owner_uuid": user.uuid},
            )
            for projects in projects
        ]
