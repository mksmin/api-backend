from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.managers.base import BaseCRUDManager
from core.database import User
from schemas.users import UserCreateModel


class UserManager(BaseCRUDManager[User]):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=User,
        )

    async def create(
        self,
        user_create: UserCreateModel,
    ) -> User:
        instance_create = self.model(**user_create.model_dump())
        self.session.add(instance_create)
        return instance_create

    async def _get_by(
        self,
        field: str,
        value: int | UUID,
    ) -> User | None:
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        return await self._get_by("id", user_id)

    async def get_by_uuid(
        self,
        user_uuid: UUID,
    ) -> User | None:
        return await self._get_by("uuid", user_uuid)

    async def get_by_tg_id(
        self,
        user_tg_id: int,
    ) -> User | None:
        return await self._get_by("tg_id", user_tg_id)
