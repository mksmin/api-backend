import logging
import uuid
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from typing import (
    Annotated,
    Any,
)

import jwt
from fastapi import (
    Cookie,
    Depends,
    HTTPException,
    status,
)
from jwt import (
    ExpiredSignatureError,
    InvalidTokenError,
)

from core.config import settings

log = logging.getLogger(__name__)


BOT_CONFIG: dict[
    str,
    dict[str, str],
] = {
    "bot1": {
        "name": "atomlabrf_bot",
        "redirect_url": "/profile",
    },
    "bot2": {
        "name": "mininwork_bot",
        "redirect_url": "/affirmations",
    },
    "bot3": {
        "name": "test_mininBot",
        "redirect_url": "/projects",
    },
    "bot4": {
        "name": "testminin2_bot",
        "redirect_url": "/projects",
    },
}


async def sign_jwt_token(
    user_id: int,
) -> dict[str, str | int]:

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
        payload=payload,
        key=settings.access_token.secret,
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

        log_message = datetime.fromtimestamp(expires_at, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S",
        )
        log.info("Token expired at: %s", log_message)

    except ExpiredSignatureError as ex_e:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex_e

    except InvalidTokenError as e:
        log.exception("Invalid token")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    else:
        return {
            "success": True,
            "user_id": user_id,
            "jti": jti,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }


async def parse_access_token(
    access_token: str | None = Cookie(
        default=None,
        alias="access_token",
    ),
) -> int | None:
    if not access_token:
        return None
    try:
        payload = await decode_jwt(access_token)
        user_id: int = payload["user_id"]
        log.info("Check access token for user_id: %s", user_id)

    except (ExpiredSignatureError, InvalidTokenError):
        log.exception("Error while decoding token")
        return None
    else:
        return user_id


async def strict_validate_access_token(
    user_id: Annotated[
        str | None,
        Depends(parse_access_token),
    ],
) -> str:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return user_id


async def soft_validate_access_token(
    user_id: str | None = Depends(parse_access_token),
) -> str | None:
    return user_id
