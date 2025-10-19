from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.managers import BaseCRUDManager
from core.database import Project
from schemas import ProjectCreateModel


class ProjectManager(BaseCRUDManager[Project]):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=Project,
        )

    async def create(
        self,
        project_create: ProjectCreateModel,
    ) -> Project:
        instance_create = self.model(**project_create.model_dump())
        self.session.add(instance_create)
        return instance_create

    async def delete(self) -> None:
        pass

    async def get_all_projects(self) -> list[Project]:
        pass

    async def get_project_by_field(
        self,
        owner_id: int,
        field: str,
        value: str,
    ) -> Project | None:
        model_field = getattr(self.model, field)
        stmt = select(self.model).where(
            func.lower(model_field) == value.lower(),
            self.model.owner_id == owner_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
