# import lib

from pydantic import ValidationError, UUID4
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar

# import from modules
from app.core.config import logger
from app.core.database import User, Project
from app.core.database.schemas import UserSchema, ProjectSchema
from .managers import BaseCRUDManager, ModelType, APIKeyManager

from .. import db_helper


def format_validation_error(exc: ValidationError) -> str:
    errors = []
    for error in exc.errors():
        field = ".".join(map(str, error["loc"]))
        msg = error["msg"]
        errors.append(f"{field}: {msg}")
    return "; ".join(errors)


class UserManager(BaseCRUDManager[User]):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory, model=User)

    async def get_one(self, value: str | int, field: str = "tg_id") -> ModelType | None:
        logger.info(f"Start searching user with ({field}: {value})")
        result = await super().get_one(field, value)
        logger.info(f"Result: {result}")
        return result

    async def create(self, data: dict) -> User:
        data["uuid"] = db_helper.generate_uuid()
        result = await self._validate_user_data(data)
        exists = await self.exists_by_field("tg_id", int(data["tg_id"]))
        if exists:
            return await super().get_one("tg_id", int(data["tg_id"]))

        return await super().create(**result)

    @staticmethod
    async def _validate_user_data(data: dict):
        try:
            user_schema = UserSchema(**data)
            return user_schema.model_dump()

        except ValidationError as e:
            error_message = format_validation_error(e)
            logger.error(f"Validation errors: {error_message}")
            raise ValueError(f"Ошибки валидации: {error_message}")


class ProjectManager(BaseCRUDManager[Project]):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory, model=Project)

    async def create(self, data: dict) -> Project:
        user_manager = UserManager(db_helper.session_factory)
        user = await user_manager.get_one("tg_id", int(data["prj_owner"]))
        if not user:
            raise ValueError(
                f"Пользователь с id = {data['prj_owner']} не найден в базе данных"
            )
        data["prj_owner"] = user.id

        return await super().create(**data)

    async def delete(
        self,
        value: int,
        field: str = "id",
    ) -> None:
        await super().delete(field, value)

    async def get_all(self, owner_id: int) -> list[Project]:
        async with self._get_session() as session:
            query = (
                select(self.model)
                .where(self.model.deleted_at.is_(None))
                .where(self.model.prj_owner == owner_id)
            )
            result = await session.execute(query)
            projects = result.scalars().all()
            if not projects:
                raise ValueError(f"У пользователя с id = {owner_id} нет проектов")
            return projects

    async def get_project_by_id(
        self,
        owner_id: int | None = None,
        project_id: int | None = None,
        project_uuid: UUID4 = None,
    ) -> list[Project]:
        if not project_id and not project_uuid:
            raise ValueError(
                "Параметры project_id и project_uuid не могут быть пустыми. Должен быть передан хотя бы один."
            )

        async with self._get_session() as session:
            if not project_uuid:
                query = select(self.model).where(
                    and_(
                        self.model.deleted_at.is_(None),
                        self.model.id == project_id,
                        self.model.prj_owner == owner_id,
                    )
                )
            else:
                query = select(self.model).where(
                    and_(
                        self.model.deleted_at.is_(None),
                        self.model.uuid == project_uuid,
                    )
                )

            result = await session.execute(query)
            project = result.scalar_one_or_none()
            if not project:
                logger.error(
                    f"Проект с id = {project_id} / uuid = {str(project_uuid)[:8]} не найден у пользователя {owner_id}"
                )
                raise ValueError(
                    f"Проект с id = {project_id} / uuid = {str(project_uuid)[:8]} не найден у пользователя {owner_id}, либо удален."
                )
            return [project]

    @staticmethod
    async def _validate_project_data(data: dict):
        try:
            project_schema = ProjectSchema(**data)
            return project_schema.model_dump()

        except ValidationError as e:
            error_message = format_validation_error(e)
            logger.error(f"Validation errors: {error_message}")
            raise e


class CRUDManager:
    def __init__(self, session_factory: async_sessionmaker):
        self.user: UserManager = UserManager(session_factory)
        self.project: ProjectManager = ProjectManager(session_factory)
        self.api_keys: APIKeyManager = APIKeyManager(session_factory)


crud_manager = CRUDManager(db_helper.session_factory)
