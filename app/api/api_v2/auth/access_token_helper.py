__all__ = ("BOT_CONFIG",)

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError

from core import logger, settings

BOT_CONFIG: dict[str, dict[str, str]] = {
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


def token_response(
    token: str,
) -> dict[str, str]:
    return {
        "access_token": token,
        "token_type": "bearer",
    }


async def sign_jwt_token(
    user_id: int,
) -> dict[str, str | int]:
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
            (now + expire_delta).timestamp(),
        ),  # expiration time (время истечения)
        "jti": jti,  # JWT ID (идентификатор токена)
    }

    token = jwt.encode(
        payload,
        settings.access_token.secret,
        algorithm=settings.access_token.algorithm,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.access_token.lifetime_seconds,
        "jti": jti,
    }


async def decode_jwt(
    token: str,
) -> dict[str, Any]:
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
            f"Token expired at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}",
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


async def parse_access_token(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> int | None:
    """Middleware for checking access token from cookies"""

    if not access_token:
        return None

    try:
        payload = await decode_jwt(access_token)
        user_id: int = payload["user_id"]
        logger.info(f"Check access token for user_id: {user_id}")
        return user_id

    except (ExpiredSignatureError, InvalidTokenError) as e:
        logger.exception("Error while decoding token: %s", e)
        return None


def sign_csrf_token() -> str:
    return secrets.token_urlsafe(32)


async def strict_validate_access_token(
    user_id: str | None = Depends(parse_access_token),
) -> str:
    """
    Строгая проверка: если токен не передан, то выбрасываем ошибку
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return user_id


async def soft_validate_access_token(
    user_id: str | None = Depends(parse_access_token),
) -> str | None:
    """
    Мягкая проверка: если токен не передан, то возвращаем None
    """
    return user_id
