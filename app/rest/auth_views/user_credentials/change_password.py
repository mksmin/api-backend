from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.responses import Response

from app_exceptions.exceptions import InvalidCurrentPasswordError
from app_exceptions.exceptions import PasswordChangeConflictError
from app_exceptions.exceptions import UserUnavailableError
from auth.csrf_helper import require_auth_csrf
from core.crud import GetCRUDService
from schemas.user_credentials import ChangeUserCredentialsForm

router = APIRouter()


@router.post(
    "/change_password",
    name="user:change-password",
)
async def change_password(
    user_credentials: Annotated[
        ChangeUserCredentialsForm,
        Form(),
    ],
    user_id: Annotated[
        int,
        Depends(require_auth_csrf),
    ],
    crud_service: GetCRUDService,
) -> Response:
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
