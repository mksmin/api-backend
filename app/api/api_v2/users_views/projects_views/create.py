from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app_exceptions import InvalidUUIDError
from app_exceptions import ProjectAlreadyExistsError
from app_exceptions import UserNotFoundError
from app_exceptions.exceptions import ProjectCreationForbiddenError
from auth import jwt_helper
from schemas import ProjectCreateSchema
from schemas import ProjectReadSchema
from subprojects.lms.crud import GetLMSCRUDService

router = APIRouter()


@router.post(
    "/",
)
async def create_project(
    lms_crud_service: GetLMSCRUDService,
    project_create: ProjectCreateSchema,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
) -> ProjectReadSchema:
    try:
        result = await lms_crud_service.projects.create_project(
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
    except ProjectCreationForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        ) from e
    else:
        return result
