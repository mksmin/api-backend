# import lib
import jwt
import secrets

# import from lib
from datetime import datetime, timedelta
from fastapi import HTTPException, Cookie
from jwt import ExpiredSignatureError, InvalidTokenError

# import from modules
from app.core import settings, logger

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
    Создаёт JWT-токен для авторизации
    :param user_id: int
    :return: dict[str, str] = {"access_token": str, "token_type": "bearer"}
    """

    payload = {
        "sub": str(user_id),
        "exp": (
            datetime.now() + timedelta(seconds=settings.access_token.lifetime_seconds)
        ).timestamp(),
        "iat": datetime.now().timestamp(),  # issued at (время создания)
    }

    token = jwt.encode(
        payload, settings.access_token.secret, algorithm=settings.access_token.algorithm
    )
    return token_response(token)


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
            options={"verify_exp": True},
        )
        return {
            "success": True,
            "user_id": decoded_token["sub"],
            "issued_at": decoded_token["iat"],
            "expires_at": decoded_token["exp"],
        }
    except ExpiredSignatureError:
        print(f"Token ExpiredSignatureError")
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError:
        print(f"Token InvalidTokenError")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def check_access_token(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> str | bool:
    """Middleware for checking access token from cookies"""
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
