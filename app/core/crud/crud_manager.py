import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.database.db_helper import db_helper
from core.database.projects import Project

from .managers import APIKeyManagerOld, BaseCRUDManagerOld

log = logging.getLogger(__name__)


class ProjectManagerOld(BaseCRUDManagerOld[Project]):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(session_factory, model=Project)

    async def delete(
        self,
        field: str,
        value: int,  # type: ignore[override]
    ) -> None:
        await super().delete(field, value)


class CRUDManager:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.project: ProjectManagerOld = ProjectManagerOld(session_factory)
        self.api_keys: APIKeyManagerOld = APIKeyManagerOld(session_factory)


crud_manager = CRUDManager(db_helper.session_factory)
