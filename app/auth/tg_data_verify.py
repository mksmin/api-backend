import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qsl

log = logging.getLogger(__name__)


def _verify_tg_signature(
    data: dict[str, str],
    secret_key: bytes,
) -> bool:
    received_hash: str = data.pop("hash", "")
    if not received_hash:
        return False

    data_check_str = "\n".join(f"{k}={data[k]}" for k in sorted(data))
    calculated_hash = hmac.new(
        secret_key,
        data_check_str.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(calculated_hash, received_hash)


def verification_mini_apps_data(
    raw_user_data: str,
    bot_token: str,
) -> bool:
    try:
        pairs = parse_qsl(
            raw_user_data,
            keep_blank_values=True,
        )
        data_dict = dict(pairs)

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256,
        ).digest()

        return _verify_tg_signature(
            data=data_dict,
            secret_key=secret_key,
        )

    except (ValueError, KeyError, TypeError) as e:
        msg_error = f"Verification error: {e}"
        raise ValueError(msg_error) from e


def verification_widget_data(
    raw_user_data: str,
    bot_token: str,
) -> bool:
    try:
        data_dict = json.loads(raw_user_data)
        secret_key = hashlib.sha256(
            bot_token.encode(),
        ).digest()

        return _verify_tg_signature(
            data=data_dict,
            secret_key=secret_key,
        )

    except (ValueError, KeyError, TypeError) as e:
        msg_error = f"Widget verification error: {e}"
        raise ValueError(msg_error) from e
