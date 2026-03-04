import hashlib
import time
from typing import Any

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth.verifiers.base import AuthStrategy
from auth.verifiers.base import TelegramWidgetPayload
from auth.verifiers.depends import verify_tg_signature
from config import settings


class TelegramWidgetVerifier(AuthStrategy[TelegramWidgetPayload]):
    AUTH_DATA_EXPIRY = 86400

    @classmethod
    def factory(
        cls,
        **_: str,
    ) -> "TelegramWidgetVerifier":
        return cls()

    async def verify(
        self,
        payload: TelegramWidgetPayload,
    ) -> dict[str, Any]:
        if not payload:
            error_msg = "Empty data provided"
            raise InvalidPayloadError(error_msg)

        bot_config = settings.bots.get(payload.bot_name)
        if not bot_config:
            error_msg = "Invalid bot_name provided"
            raise InvalidPayloadError(error_msg)

        bot_token = str(bot_config.token.get_secret_value())

        user_data = payload.data

        auth_date = int(user_data.get("auth_date", "0"))
        if time.time() - auth_date > self.AUTH_DATA_EXPIRY:
            error_msg = "Telegram widget data has expired"
            raise InvalidSignatureError(error_msg)

        secret_key = hashlib.sha256(
            bot_token.encode(),
        ).digest()

        is_valid = verify_tg_signature(
            user_data,
            secret_key,
        )
        if not is_valid:
            error_msg = "Invalid telegram widget signature"
            raise InvalidSignatureError(error_msg)

        user_data["tg_id"] = user_data.pop("id")

        return user_data
