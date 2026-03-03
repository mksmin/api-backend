import hashlib
from typing import Any

from pydantic import SecretStr

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth.verifiers.base import AuthStrategy
from auth.verifiers.depends import verify_tg_signature
from config import settings
from config.auth_bots import BotsEnum


class TelegramWidgetVerifier(AuthStrategy):
    def __init__(self, bot_token: str | SecretStr) -> None:
        if isinstance(bot_token, SecretStr):
            bot_token = bot_token.get_secret_value()

        self._bot_token = bot_token

    @classmethod
    def factory(
        cls,
        bot_name: BotsEnum,
        **_: str,
    ) -> "TelegramWidgetVerifier":
        config = settings.bots[bot_name]
        return cls(bot_token=config.token)

    async def verify(
        self,
        raw_data: dict[str, Any],
    ) -> dict[str, Any]:
        if not raw_data:
            error_msg = "Empty data provided"
            raise InvalidPayloadError(error_msg)

        secret_key = hashlib.sha256(
            self._bot_token.encode(),
        ).digest()

        is_valid = verify_tg_signature(
            raw_data,
            secret_key,
        )
        if not is_valid:
            raise InvalidSignatureError

        raw_data["tg_id"] = raw_data.pop("id")

        return raw_data
