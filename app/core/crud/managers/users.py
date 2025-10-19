from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.managers.base import BaseCRUDManager
from core.database import User


class UserManager(BaseCRUDManager[User]):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=User,
        )

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        stmt = select(self.model).where(self.model.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_uuid(
        self,
        user_uuid: UUID,
    ) -> User | None:
        stmt = select(self.model).where(self.model.uuid == user_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tg_id(
        self,
        user_tg_id: int,
    ) -> User | None:
        stmt = select(self.model).where(self.model.tg_id == user_tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
