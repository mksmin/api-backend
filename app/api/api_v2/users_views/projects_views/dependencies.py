from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app_exceptions import InvalidUUIDError
from app_exceptions import ProjectNotFoundError
from app_exceptions import UserNotFoundError
from auth import jwt_helper
from schemas import ProjectReadSchema
from schemas.projects import LMSProjectReadSchema
from subprojects.lms.crud import GetLMSCRUDService


async def get_user_projects(
    lms_crud_service: GetLMSCRUDService,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
) -> list[LMSProjectReadSchema]:
    try:
        return await lms_crud_service.projects.get_all(
            int(user_id),
        )

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e


async def get_project_by_uuid(
    project_uuid: str,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
    lms_crud_service: GetLMSCRUDService,
) -> ProjectReadSchema | None:
    try:
        project = await lms_crud_service.projects.get_by_uuid(
            user_id=int(user_id),
            project_uuid=project_uuid,
        )
    except (ProjectNotFoundError, InvalidUUIDError):
        return None
    else:
        return ProjectReadSchema.model_validate(project)


async def delete_project_by_uuid(
    project_uuid: str,
    user_id: Annotated[
        str,
        Depends(jwt_helper.strict_validate_access_token),
    ],
    lms_crud_service: GetLMSCRUDService,
) -> None:
    try:
        await lms_crud_service.projects.delete_project(
            user_id=int(user_id),
            project_uuid=project_uuid,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
