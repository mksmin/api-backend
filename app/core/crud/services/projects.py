from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v2.dependencies import validate_uuid_str
from app_exceptions import (
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
        project_uuid_validated = validate_uuid_str(project_uuid)
        user = await self.user_manager.get_by_id(user_id)
        if not user:
            raise UserNotFoundError

        project = await self.manager.get_by_uuid(project_uuid_validated)
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
