import hashlib
import hmac
import secrets

from core.config import settings


async def generate_api_key_and_hash() -> tuple[str, str]:
    """
    Generate a random string and hmac hash for api key.

    This function generates a random string using the secrets module
    and creates a hmac hash using the generated string
    and a secret key from the settings.
    The function returns a tuple containing the generated string and the hmac hash.

    :return: A tuple containing the generated string and the hmac hash.
    """
    raw_key = f"mks_{secrets.token_urlsafe(32)}"
    digest: str = hmac.new(
        settings.access_token.secret.encode(),
        raw_key.encode(),
        hashlib.sha256,
    ).hexdigest()
    return raw_key, digest
