from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v2.dependencies import validate_uuid_str
from app_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from core.crud.managers import UserManager
from schemas import UserReadSchema, UserSchema
from schemas.users import UserCreateModel, UserCreateSchema


class UserService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.manager = UserManager(self.session)

    async def create_user(
        self,
        user_create: UserCreateSchema,
    ) -> UserSchema:
        user_exists = await self.manager.get_by_tg_id(user_create.tg_id)
        if user_exists:
            raise UserAlreadyExistsError

        user_create_model = UserCreateModel.model_validate(user_create)
        user = await self.manager.create(user_create_model)

        await self.session.commit()

        return UserSchema.model_validate(user)

    async def get_by_id_or_uuid(
        self,
        user_id: int | str,
    ) -> UserReadSchema:
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
    ) -> UserSchema:
        user = await self.manager.get_by_tg_id(tg_id)
        try:
            return UserSchema.model_validate(user)
        except ValidationError as e:
            raise UserNotFoundError from e
