from typing import Annotated

from fastapi import Depends, HTTPException, status

from api.api_v2.auth import token_utils
from app_exceptions import ProjectNotFoundError, UserNotFoundError
from core.crud import GetCRUDService, crud_manager
from schemas import ProjectReadSchema


async def get_user_projects(
    crud_service: GetCRUDService,
    user_id: Annotated[
        str,
        Depends(token_utils.strict_validate_access_token),
    ],
) -> list[ProjectReadSchema]:
    try:
        return await crud_service.project.get_all(int(user_id))

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e


async def get_project_by_uuid(
    project_uuid: str,
    user_id: Annotated[
        str,
        Depends(token_utils.strict_validate_access_token),
    ],
    crud_service: GetCRUDService,
) -> ProjectReadSchema:
    project = await crud_service.project.get_by_uuid(user_id, project_uuid)
    return ProjectReadSchema.model_validate(project)


async def delete_project_by_uuid(
    project_uuid: str,
    user_id: Annotated[
        str,
        Depends(token_utils.strict_validate_access_token),
    ],
    crud_service: GetCRUDService,
) -> bool:
    try:
        project = await crud_service.project.get_by_uuid(
            user_id=user_id,
            project_uuid=project_uuid,
        )

        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для удаления проекта",
            )
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект с таким uuid не найден",
        ) from e
    else:
        await crud_manager.project.delete("id", project.id)
        return True
