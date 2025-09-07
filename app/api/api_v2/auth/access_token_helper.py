# import lib
import jwt
import secrets
import uuid

# import from lib
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Cookie, Depends, status
from jwt import ExpiredSignatureError, InvalidTokenError, MissingRequiredClaimError

# import from modules
from core import settings, logger

BOT_CONFIG = {
    "bot1": {
        "name": "atombot",
        "redirect_url": "/profile",
    },
    "bot2": {
        "name": "mininbot",
        "redirect_url": "/affirmations",
    },
    "bot3": {
        "name": "testbot",
        "redirect_url": "/profile",
    },
}


def token_response(token: str) -> dict:
    return {"access_token": token, "token_type": "bearer"}


async def sign_jwt_token(user_id: int) -> dict:
    """
    Создаёт JWT access-токен для авторизации
    :param user_id: int
    :return: dict[str, str] = {"access_token": str, "token_type": "bearer"}
    """

    now = datetime.now(timezone.utc)
    expire_delta = timedelta(seconds=settings.access_token.lifetime_seconds)
    jti = str(uuid.uuid4())

    payload = {
        "iss": "mks-min.ru",  # issuer (эмитент)
        "sub": str(user_id),  # subject (идентификатор субъекта)
        "iat": int(now.timestamp()),  # issued at (время создания)
        "exp": int(
            (now + expire_delta).timestamp()
        ),  # expiration time (время истечения)
        "jti": jti,  # JWT ID (идентификатор токена)
    }

    token = jwt.encode(
        payload, settings.access_token.secret, algorithm=settings.access_token.algorithm
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.access_token.lifetime_seconds,
        "jti": jti,
    }


async def decode_jwt(token: str) -> dict:
    """
    Decodes a JWT token and returns a dictionary with the decoded token information.

    :param token: (str) The JWT token to be decoded.
    :return: (dict) A dictionary with the decoded token information.
    :raises: (HTTPException) If the token is expired or invalid.
    """

    try:
        decoded_token = jwt.decode(
            token,
            settings.access_token.secret,
            algorithms=[settings.access_token.algorithm],
            options={"require": ["exp", "iat", "sub", "jti"]},
        )
        jti = decoded_token["jti"]
        user_id = int(decoded_token["sub"])
        issued_at = int(decoded_token["iat"])
        expires_at = int(decoded_token["exp"])

        logger.info(
            f"Token expired at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return {
            "success": True,
            "user_id": user_id,
            "jti": jti,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }

    except ExpiredSignatureError:
        print(f"Token ExpiredSignatureError")
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        logger.exception(f"Invalid token: {e}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def check_access_token(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> str | bool:
    """Middleware for checking access token from cookies"""

    logger.debug(f"Check access token: {access_token}")
    if not access_token:
        return False

    try:
        payload = await decode_jwt(access_token)

        user_id: str = payload.get("user_id")
        logger.info(f"Check access token for user_id: {user_id}")
        if not user_id:
            return False
        return access_token

    except HTTPException as he:
        logger.error(f"Error in middleware: {he}", exc_info=True)
        return False


async def sign_csrf_token():
    return secrets.token_urlsafe(32)


async def validate_access_token_dependency(
    access_token: str | bool = Depends(check_access_token),
) -> str:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return access_token
