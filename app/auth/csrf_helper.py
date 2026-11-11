import hmac
import time
from typing import Annotated

from fastapi import Cookie
from fastapi import HTTPException
from fastapi import status
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request

from auth import jwt_helper
from config import settings

CSRF_COOKIE_NAME = "fastapi-csrf-token"
CSRF_MAX_AGE = settings.access_token.lifetime_seconds


def get_or_create_login_csrf(
    request: Request,
    csrf: CsrfProtect,
) -> tuple[str, str | None]:
    now = int(time.time())
    state = request.session.get("_csrf")

    if (
        not isinstance(state, dict)
        or state.get("scope") != "anonymous"
        or not isinstance(state.get("issued_at"), int)
        or not isinstance(state.get("token"), str)
        or not isinstance(state.get("signed"), str)
        or now - state["issued_at"] >= CSRF_MAX_AGE
    ):
        token, signed = csrf.generate_csrf_tokens()

        request.session["_csrf"] = {
            "token": token,
            "signed": signed,
            "scope": "anonymous",
            "issued_at": now,
        }
        return token, signed

    if request.cookies.get(CSRF_COOKIE_NAME) != state["signed"]:
        return state["token"], state["signed"]

    return state["token"], None


def csrf_token_for(jti: str) -> str:
    key = settings.secrets.csrf_secret.get_secret_value().encode()
    return hmac.digest(key, f"csrf:v1:{jti}".encode(), "sha256").hex()


async def require_auth_csrf(
    request: Request,
    access_token: Annotated[
        str | None,
        Cookie(),
    ] = None,
) -> int:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    claims = await jwt_helper.decode_jwt(
        access_token,
    )
    async with request.form() as form:
        submitted = form.get("token_key")

    expected = csrf_token_for(claims["jti"])
    if (
        not isinstance(submitted, str)
        or not hmac.compare_digest(submitted.encode(), expected.encode())
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid_csrf_token",
        )

    return int(claims["user_id"])
