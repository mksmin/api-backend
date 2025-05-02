# import lib
from contextlib import asynccontextmanager
from datetime import datetime

from pydantic import ValidationError, UUID4
from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar, Generic, Type, AsyncIterator, cast

# import from modules
from app.core.config import logger
from app.core.database import User, Project
from app.core.database.schemas import UserSchema, ProjectSchema

from .. import db_helper

ModelType = TypeVar("ModelType")


def format_validation_error(exc: ValidationError) -> str:
    errors = []
    for error in exc.errors():
        field = ".".join(map(str, error["loc"]))
        msg = error["msg"]
        errors.append(f"{field}: {msg}")
    return "; ".join(errors)


class BaseCRUDManager(Generic[ModelType]):
    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession], model: Type[ModelType]
    ):
        self.session_factory = session_factory
        self.model = model

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Ошибка при работе с базой данных")
                raise

    async def exists_by_field(self, field: str, value: str | int) -> bool | ModelType:
        async with self._get_session() as session:
            session = cast(
                AsyncSession, session
            )  # asynccontextmanager не передает аннотацию AsyncSession, поэтому явно указываем
            query = select(self.model).where(getattr(self.model, field) == value)
            result = await session.execute(query)
            return result.scalar_one_or_none() is not None

    async def create(self, **kwargs) -> ModelType:
        async with self._get_session() as session:
            session = cast(AsyncSession, session)
            instance = self.model(**kwargs)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            logger.info(f"Created {self.model.__name__} with id: {instance.id}")
            return instance

    async def get_one(self, field: str, value: str | int) -> ModelType | None:
        result = await self.exists_by_field(field, value)
        if result:
            async with self._get_session() as session:
                query = select(self.model).where(getattr(self.model, field) == value)
                result = await session.execute(query)
                return result.scalar_one_or_none()

        return result

    async def delete(self, field: str, value: str | int) -> None:
        async with self._get_session() as session:
            query = (
                update(self.model)
                .where(
                    and_(
                        getattr(self.model, field) == value,
                        self.model.deleted_at.is_(None),
                    )
                )
                .values(deleted_at=datetime.now())
            )
            try:
                result = await session.execute(query)
                if result.rowcount == 0:
                    if await self.exists_by_field(field, value):
                        raise ValueError(f"Объект с {field} = {value} уже удален")
                    else:
                        raise ValueError(f"Объект с {field} = {value} не найден")

            except SQLAlchemyError as e:
                await session.rollback()
                raise RuntimeError(f"Ошибка при удалении объекта: {str(e)}")


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
                raise ValueError(
                    f"Проект с id = {project_id} не найден у пользователя {owner_id}, либо удален."
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


crud_manager = CRUDManager(db_helper.session_factory)
