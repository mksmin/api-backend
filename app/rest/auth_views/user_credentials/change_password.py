from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi_csrf_protect import CsrfProtect

from app_exceptions.exceptions import InvalidCurrentPasswordError
from app_exceptions.exceptions import PasswordChangeConflictError
from app_exceptions.exceptions import UserUnavailableError
from auth import jwt_helper
from core.crud import GetCRUDService
from schemas.user_credentials import ChangeUserCredentialsForm

router = APIRouter()


@router.post(
    "/change_password",
    name="user:change-password",
)
async def change_password(
    request: Request,
    user_credentials: Annotated[
        ChangeUserCredentialsForm,
        Form(),
    ],
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
    user_id: Annotated[
        int,
        Depends(
            jwt_helper.strict_validate_access_token,
        ),
    ],
    crud_service: GetCRUDService,
) -> Response:
    await csrf_protect.validate_csrf(request)

    try:
        await crud_service.user_credential.change_user_password(
            user_id,
            user_credentials,
        )
    except UserUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc
    except InvalidCurrentPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid_current_password",
        ) from exc
    except PasswordChangeConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="password_change_conflict",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
