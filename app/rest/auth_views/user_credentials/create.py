from typing import Annotated

from fastapi import APIRouter
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect

from app_exceptions.exceptions import CredentialAlreadyExistsError
from app_exceptions.exceptions import UserUnavailableError
from auth import jwt_helper
from core.crud import GetCRUDService
from schemas.user_credentials import CreateCredentialsForm
from schemas.user_credentials import LoginCredentialsForm

router = APIRouter()


@router.post(
    "/create-credentials",
    name="user:create-credentials",
)
async def create_credentials(
    request: Request,
    user_credentials_in: Annotated[
        CreateCredentialsForm,
        Form(),
    ],
    user_id: Annotated[
        int,
        Depends(
            jwt_helper.strict_validate_access_token,
        ),
    ],
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
    crud_service: GetCRUDService,
) -> JSONResponse:
    await csrf_protect.validate_csrf(request)
    try:
        await crud_service.user_credential.create_user_credentials(
            user_id,
            user_credentials_in,
        )
    except UserUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc
    except CredentialAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credential already exists or email used",
        ) from exc

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": user_id,
            "email": user_credentials_in.email,
        },
    )


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
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "id": user.id,
            "username": user.username,
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )
