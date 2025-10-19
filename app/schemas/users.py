from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """
    Базовая схема для модели пользователя
    """

    first_name: str | None
    last_name: str | None
    tg_id: int
    username: str | None

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBase):
    """
    Схема создания пользователя
    """


class UserReadSchema(UserBase):
    """
    Схема чтения пользователя
    """

    uuid: UUID
    created_at: datetime


class UserSchema(UserBase):
    """
    Полная схема пользователя для внутреннего использования
    """

    id: int
    uuid: UUID
    created_at: datetime
    deleted_at: datetime | None
