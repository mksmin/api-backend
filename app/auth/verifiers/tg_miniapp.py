import hashlib
import hmac
import json
from typing import Any
from urllib.parse import parse_qsl

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth.verifiers.base import BaseVerifier
from auth.verifiers.depends import verify_tg_signature


class TelegramMiniAppVerifier(BaseVerifier):
    def verify(
        self,
        raw_data: str,
    ) -> dict[str, Any]:
        if not raw_data:
            error_msg = "Empty data provided"
            raise InvalidPayloadError(error_msg)

        try:
            pairs = parse_qsl(
                raw_data,
                keep_blank_values=True,
            )
            data_dict = dict(pairs)

        except (ValueError, TypeError, KeyError) as e:
            msg_error = "Invalid miniapp payload format"
            raise InvalidSignatureError(msg_error) from e

        secret_key = hmac.new(
            b"WebAppData",
            self._bot_token.encode(),
            hashlib.sha256,
        ).digest()

        is_valid = verify_tg_signature(
            data_dict,
            secret_key,
        )
        if not is_valid:
            raise InvalidSignatureError

        user_data: dict[str, Any] = json.loads(data_dict["user"])
        user_data["tg_id"] = user_data.pop("id")
        return user_data
