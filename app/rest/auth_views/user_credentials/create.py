from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse

from app_exceptions.exceptions import CredentialAlreadyExistsError
from app_exceptions.exceptions import UserUnavailableError
from auth.csrf_helper import require_auth_csrf
from core.crud import GetCRUDService
from schemas.user_credentials import CreateCredentialsForm

router = APIRouter()


@router.post(
    "/create-credentials",
    name="user:create-credentials",
)
async def create_credentials(
    user_credentials_in: Annotated[
        CreateCredentialsForm,
        Form(),
    ],
    user_id: Annotated[
        int,
        Depends(require_auth_csrf),
    ],
    crud_service: GetCRUDService,
) -> JSONResponse:
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
