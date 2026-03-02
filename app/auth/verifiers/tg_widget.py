import hashlib
from typing import Any

from app_exceptions import InvalidPayloadError
from app_exceptions import InvalidSignatureError
from auth.verifiers.base import BaseVerifier
from auth.verifiers.depends import verify_tg_signature


class TelegramWidgetVerifier(BaseVerifier):
    def verify(
        self,
        data_dict: dict[str, Any],
    ) -> dict[str, Any]:
        if not data_dict:
            error_msg = "Empty data provided"
            raise InvalidPayloadError(error_msg)

        secret_key = hashlib.sha256(
            self._bot_token.encode(),
        ).digest()

        is_valid = verify_tg_signature(
            data_dict,
            secret_key,
        )
        if not is_valid:
            raise InvalidSignatureError

        data_dict["tg_id"] = data_dict.pop("id")

        return data_dict
