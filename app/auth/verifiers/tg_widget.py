import hashlib
import json
from typing import Any

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth.verifiers.base import BaseVerifier
from auth.verifiers.depends import verify_tg_signature


class TelegramWidgetVerifier(BaseVerifier):
    def verify(
        self,
        raw_data: str,
    ) -> None:
        if not raw_data:
            raise InvalidPayloadError("Empty data provided")

        try:
            data_dict = json.loads(raw_data)
        except (ValueError, TypeError) as e:
            msg_error = "Invalid JSON payload format"
            raise InvalidPayloadError(msg_error) from e

        secret_key = hashlib.sha256(
            self._bot_token.encode(),
        ).digest()

        is_valid = verify_tg_signature(
            data_dict,
            secret_key,
        )
        if not is_valid:
            raise InvalidSignatureError()

        return
