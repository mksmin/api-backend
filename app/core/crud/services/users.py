from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v2.dependencies import validate_uuid_str
from app_exceptions import (
    UserNotFoundError,
)
from core.crud.managers import UserManager
from schemas import UserReadSchema


class UserService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.manager = UserManager(session)

    async def get_by_id_or_uuid(
        self,
        user_id: int | str,
    ) -> UserReadSchema | None:
        if isinstance(user_id, str):
            user_uuid = validate_uuid_str(user_id)
            user = await self.manager.get_by_uuid(user_uuid)
        else:
            user = await self.manager.get_by_id(user_id)

        try:
            return UserReadSchema.model_validate(user)
        except ValidationError as e:
            raise UserNotFoundError from e

    async def get_by_tg_id(
        self,
        tg_id: int,
    ) -> UserReadSchema | None:
        user = await self.manager.get_by_tg_id(tg_id)
        try:
            return UserReadSchema.model_validate(user)
        except ValidationError as e:
            raise UserNotFoundError from e
