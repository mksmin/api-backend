import hashlib
import hmac
import secrets

from app.core import settings


async def generate_api_key():
    raw_key = secrets.token_urlsafe(32)
    digest = hmac.new(
        settings.access_token.secret.encode(), raw_key.encode(), hashlib.sha256
    ).hexdigest()
    return {"api_key": raw_key, "digest": digest}
