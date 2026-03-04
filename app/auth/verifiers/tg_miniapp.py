import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth.verifiers.base import AuthStrategy
from auth.verifiers.base import TelegramMiniappPayload
from auth.verifiers.depends import verify_tg_signature
from config import settings


class TelegramMiniAppVerifier(AuthStrategy[TelegramMiniappPayload]):
    AUTH_DATA_EXPIRY = 86400

    @classmethod
    def factory(
        cls,
        **_: str,
    ) -> "TelegramMiniAppVerifier":
        return cls()

    async def verify(
        self,
        payload: TelegramMiniappPayload,
    ) -> dict[str, Any]:
        if not payload:
            error_msg = "Empty data provided"
            raise InvalidPayloadError(error_msg)

        bot_config = settings.bots.get(payload.bot_name)
        if not bot_config:
            error_msg = "Invalid bot_name provided"
            raise InvalidPayloadError(error_msg)

        bot_token = str(bot_config.token.get_secret_value())

        try:
            pairs = parse_qsl(
                payload.data,
                keep_blank_values=True,
            )
            data_dict = dict(pairs)

        except (ValueError, TypeError, KeyError) as e:
            msg_error = "Invalid miniapp payload format"
            raise InvalidSignatureError(msg_error) from e

        auth_date = int(data_dict.get("auth_date", "0"))
        if time.time() - auth_date > self.AUTH_DATA_EXPIRY:
            error_msg = "Authentication data has expired"
            raise InvalidSignatureError(error_msg)

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256,
        ).digest()

        is_valid = verify_tg_signature(
            data_dict,
            secret_key,
        )
        if not is_valid:
            error_msg = "Invalid Telegram signature"
            raise InvalidSignatureError(error_msg)

        user_data: dict[str, Any] = json.loads(data_dict["user"])
        user_data["tg_id"] = user_data.pop("id")
        return user_data
