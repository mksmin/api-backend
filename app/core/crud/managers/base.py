from contextlib import asynccontextmanager
from datetime import datetime
from typing import Generic, Type, AsyncIterator, cast, TypeVar, TYPE_CHECKING

from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core import logger

from core.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


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

    async def exists_by_field(self, field: str, value: str | int) -> bool:
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
            logger.info(f"Created {self.model.__name__} with id: {instance.id}")  # type: ignore[attr-defined]
            return instance

    async def get_one(self, field: str, value: str | int) -> ModelType | None:
        async with self._get_session() as session:
            session = cast(AsyncSession, session)
            query = select(self.model).where(getattr(self.model, field) == value)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def delete(self, field: str, value: str | int) -> None:
        async with self._get_session() as session:
            query = (
                update(self.model)
                .where(
                    and_(
                        getattr(self.model, field) == value,
                        self.model.deleted_at.is_(None),  # type: ignore[attr-defined]
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
