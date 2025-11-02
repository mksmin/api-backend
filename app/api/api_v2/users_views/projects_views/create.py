from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app_exceptions import (
    InvalidUUIDError,
    ProjectAlreadyExistsError,
    UserNotFoundError,
)
from auth import jwt_helper
from core.crud import GetCRUDService
from schemas import ProjectCreateSchema, ProjectReadSchema

router = APIRouter()


@router.post(
    "/",
)
async def create_project(
    crud_service: GetCRUDService,
    project_create: ProjectCreateSchema,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
) -> ProjectReadSchema:
    try:
        result = await crud_service.project.create_project(
            project_create=project_create,
            user_id=int(user_id),
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    except InvalidUUIDError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID",
        ) from e
    except ProjectAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project already exists",
        ) from e
    else:
        return result
