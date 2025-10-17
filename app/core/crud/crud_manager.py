import logging
from collections.abc import Sequence
from typing import Any

from pydantic import UUID4, ValidationError
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.database import User
from core.database.db_helper import db_helper
from core.database.projects import Project
from core.database.schemas import ProjectSchema, UserSchema

from .managers import APIKeyManager, BaseCRUDManager

log = logging.getLogger(__name__)


def format_validation_error(exc: ValidationError) -> str:
    errors = []
    for error in exc.errors():
        field = ".".join(map(str, error["loc"]))
        msg = error["msg"]
        errors.append(f"{field}: {msg}")
    return "; ".join(errors)


class UserManager(BaseCRUDManager[User]):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(session_factory, model=User)

    async def get_one(
        self,
        field: str = "tg_id",
        value: str | int = ...,  # type: ignore[assignment]
    ) -> User | None:
        log.info("Start searching user with (%s: %s)", field, value)
        result = await super().get_one(field, value)
        log.info("Result: %s", result)
        return result

    async def create(  # type: ignore[override]
        self,
        data: dict[str, Any],
    ) -> User:
        data["uuid"] = db_helper.generate_uuid()
        result = await self._validate_user_data(data)
        exists = await self.exists_by_field("tg_id", int(data["tg_id"]))
        if exists:
            return await super().get_one("tg_id", int(data["tg_id"]))  # type: ignore[return-value]

        return await super().create(**result)

    @staticmethod
    async def _validate_user_data(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            user_schema = UserSchema(**data)
            return user_schema.model_dump()

        except ValidationError as e:
            error_message = format_validation_error(e)
            except_msg = "Ошибка валидации:" + error_message
            log.exception("Validation errors: %s", error_message)
            raise ValueError(except_msg) from e


class ProjectManager(BaseCRUDManager[Project]):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(session_factory, model=Project)

    async def create(  # type: ignore[override]
        self,
        data: dict[str, Any],
    ) -> Project:
        user_manager = UserManager(db_helper.session_factory)
        user = await user_manager.get_one("tg_id", int(data["owner_id"]))
        if not user:
            msg_error = (
                f"Пользователь с id = {data['prj_owner']} не найден в базе данных"
            )
            raise ValueError(msg_error)
        data["owner_id"] = user.id

        return await super().create(**data)

    async def delete(
        self,
        field: str,
        value: int,  # type: ignore[override]
    ) -> None:
        await super().delete(field, value)

    async def get_all(self, owner_id: int) -> Sequence[Project]:
        async with self._get_session() as session:
            query = (
                select(self.model)
                .where(self.model.deleted_at.is_(None))
                .where(self.model.owner_id == owner_id)
            )
            result = await session.execute(query)
            return result.scalars().all()

    async def get_project_by_id(
        self,
        owner_id: int | None = None,
        project_id: int | None = None,
        project_uuid: UUID4 | None = None,
    ) -> Project | None:
        if not project_id and not project_uuid:
            msg_error = (
                "Параметры project_id и project_uuid не могут быть пустыми. "
                "Должен быть передан хотя бы один."
            )
            raise ValueError(msg_error)

        async with self._get_session() as session:
            if not project_uuid:
                query = select(self.model).where(
                    and_(
                        self.model.deleted_at.is_(None),
                        self.model.id == project_id,
                        self.model.owner_id == owner_id,
                    ),
                )
            else:
                query = select(self.model).where(
                    and_(
                        self.model.deleted_at.is_(None),
                        self.model.uuid == project_uuid,
                    ),
                )

            result = await session.execute(query)
            project: Project | None = result.scalar_one_or_none()
            if not project:
                log.info(
                    "Проект с id=%s не найден",
                    str(project_uuid)[:8] if project_uuid else str(project_id),
                )
            return project

    @staticmethod
    async def _validate_project_data(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            project_schema = ProjectSchema(**data)
            return project_schema.model_dump()

        except ValidationError as e:
            error_message = format_validation_error(e)
            log.exception("Validation errors: %s", error_message)
            raise


class CRUDManager:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.user: UserManager = UserManager(session_factory)
        self.project: ProjectManager = ProjectManager(session_factory)
        self.api_keys: APIKeyManager = APIKeyManager(session_factory)


crud_manager = CRUDManager(db_helper.session_factory)
