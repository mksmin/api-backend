from typing import Annotated

from fastapi import APIRouter
from fastapi import Form
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from auth import jwt_helper
from config import settings
from core.crud import GetCRUDService
from schemas.user_credentials import LoginCredentialsForm

router = APIRouter()


@router.post(
    "/authenticate",
    name="user:authenticate",
)
async def authenticate_user(
    _request: Request,
    user_credentials: Annotated[
        LoginCredentialsForm,
        Form(),
    ],
    crud_service: GetCRUDService,
) -> JSONResponse:
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
            "redirect_path": "/profile",
        },
    )
    response.set_cookie(
        key="access_token",
        value=str(jwt_token.get("access_token", "")),
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=settings.access_token.lifetime_seconds,
    )
    return response
