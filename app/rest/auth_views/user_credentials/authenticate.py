from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect

from auth import jwt_helper
from auth.redirects import safe_login_redirect
from config import settings
from core.crud import GetCRUDService
from schemas.user_credentials import LoginCredentialsForm

router = APIRouter()


@router.post(
    "/authenticate",
    name="user:authenticate",
)
async def authenticate_user(
    request: Request,
    user_credentials: Annotated[
        LoginCredentialsForm,
        Form(),
    ],
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
    crud_service: GetCRUDService,
    redirect_url: Annotated[
        str | None,
        Query(),
    ] = None,
) -> JSONResponse:
    redirect_path = safe_login_redirect(redirect_url)

    await csrf_protect.validate_csrf(request)

    user = await crud_service.user_credential.authenticate_user(
        user_credentials,
    )

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "User not found!",
            },
        )

    jwt_token = await jwt_helper.sign_jwt_token(user.id)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "id": user.id,
            "username": user.username,
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "redirect_path": redirect_path,
        },
    )
    response.set_cookie(
        key="access_token",
        value=str(jwt_token.get("access_token", "")),
        httponly=True,
        secure=settings.run.auth_cookies_secure,
        samesite="lax",
        path="/",
        max_age=settings.access_token.lifetime_seconds,
    )
    return response
