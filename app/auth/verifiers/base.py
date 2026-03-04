from typing import Any
from typing import Protocol

from pydantic import BaseModel

from config.auth_bots import BotsEnum


class AuthPayload(BaseModel):
    """Base class for all authentication payloads"""


class TelegramMiniappPayload(AuthPayload):
    bot_name: BotsEnum
    data: str


class TelegramWidgetPayload(AuthPayload):
    bot_name: BotsEnum
    data: dict[str, Any]


class TelegramOIDCPayload(AuthPayload):
    bot_name: BotsEnum
    client_id: str | int
    id_token: str


class PasswordPayload(AuthPayload):
    username: str
    password: str


class AuthStrategy[T: AuthPayload](Protocol):
    async def verify(self, payload: T) -> dict[str, Any]:
        """Return true if signature is valid"""
