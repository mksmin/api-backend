import hashlib
import hmac
from collections.abc import Mapping


def verify_tg_signature(
    data: Mapping[str, str],
    secret_key: bytes,
) -> bool:
    received_hash = data.get("hash")
    if not received_hash:
        return False

    filtered_data = {k: v for k, v in data.items() if k != "hash"}

    data_check_str = "\n".join(f"{k}={filtered_data[k]}" for k in sorted(filtered_data))

    calculated_hash = hmac.new(
        secret_key,
        data_check_str.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        calculated_hash,
        received_hash,
    )
