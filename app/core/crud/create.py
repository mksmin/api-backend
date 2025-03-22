# import lib
import asyncio
from contextlib import asynccontextmanager

import asyncpg
import traceback

# import from lib
from dateutil import parser
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar, Generic, Type

# import from modules
from app.core.config import logger
from app.core.database import User, Project
from app.core.database.schemas import UserSchema
from .config import connector
from fastapi import Depends

from .. import db_helper


@connector
async def create_user_from_dict(
        session: AsyncSession,
        dict_values: dict
) -> tuple[bool, str]:
    valid_data = {
        key: (
            parser.parse(value)
            if key in ("date_bid_ya", "birth_date")
            else str(value)
            if key == "timezone"
            else value
        )
        for key, value in dict_values.items()
        if hasattr(User, key)
    }

    try:
        user = User(**valid_data)

        session.add(user)
        await session.commit()
        return True, 'Пользователь успешно создан.'

    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        logger.exception("Проблема с подключением к БД")
        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg

    except SQLAlchemyError as e:
        logger.exception("Ошибка SQLAlchemy")
        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg

    except Exception as e:
        logger.exception('Ошибка при создании пользователя')
        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg


@connector
async def create_project(
        session: AsyncSession,
        project_uuid: str,
):
    try:
        project = Project(
            uuid=project_uuid
        )
        print(f"project.uuid: {project.uuid}")
        print(f'session: {session}')
        session.add(project)
        await session.commit()
        return True, 'Проект успешно создан.'
    except SQLAlchemyError as e:
        logger.exception('Ошибка при создании проекта')

        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg

    except Exception as e:
        logger.exception('Ошибка при создании проекта')

        error_msg = f"{type(e).__name__}: {str(e)}"
        return False, error_msg


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


class CRUDManager:
    def __init__(
            self,
            session_factory: async_sessionmaker
    ):
        self.session_factory = session_factory
        self.user: UserManager = UserManager(session_factory)


crud_manager = CRUDManager(db_helper.session_factory)
