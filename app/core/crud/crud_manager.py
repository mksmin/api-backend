# import lib
from contextlib import asynccontextmanager

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar, Generic, Type

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
            self,
            session_factory: async_sessionmaker[AsyncSession],
            model: Type[ModelType]
    ):
        self.session_factory = session_factory
        self.model = model

    @asynccontextmanager
    async def _get_session(self):
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Ошибка при работе с базой данных")
                raise

    async def exists_by_field(self, field: str, value: str) -> bool:
        async with self._get_session() as session:
            query = select(self.model).where(
                getattr(self.model, field) == value
            )
            result = await session.execute(query)
            return result.scalar_one_or_none() is not None

    async def create(self, **kwargs) -> ModelType:
        async with self._get_session() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            logger.info(f'Created {self.model.__name__} with id: {instance.id}')
            return instance


class UserManager(BaseCRUDManager[User]):
    def __init__(
            self,
            session_factory: async_sessionmaker[AsyncSession]
    ):
        super().__init__(session_factory, model=User)

    async def create(self, data: dict) -> User:
        result = await self._validate_user_data(data)

        if await self.exists_by_field('id_bid_ya', result['id_bid_ya']):
            raise ValueError('Пользователь с таким id_bid_ya уже существует')

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
    def __init__(
            self,
            session_factory: async_sessionmaker[AsyncSession]
    ):
        super().__init__(session_factory, model=Project)

    async def create(self, data: dict) -> Project:
        result = await self._validate_project_data(data)

        if await self.exists_by_field('uuid', result['uuid']):
            raise ValueError('Проект с таким uuid уже существует')

        return await super().create(**result)

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
    def __init__(
            self,
            session_factory: async_sessionmaker
    ):
        self.user: UserManager = UserManager(session_factory)
        self.project: ProjectManager = ProjectManager(session_factory)


crud_manager = CRUDManager(db_helper.session_factory)
