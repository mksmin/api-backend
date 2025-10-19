from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.api_v2.auth import token_utils
from app_exceptions import UserNotFoundError
from core.crud import GetCRUDService, crud_manager
from core.database.schemas import ProjectResponseSchema
from schemas import ProjectReadSchema


async def validate_uuid_str(project_uuid: str) -> UUID:
    try:
        return UUID(project_uuid)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректный формат UUID",
        ) from e


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
    project_uuid: Annotated[UUID, Depends(validate_uuid_str)],
) -> ProjectResponseSchema:
    if project := await crud_manager.project.get_project_by_id(
        project_uuid=project_uuid,
    ):
        return ProjectResponseSchema.model_validate(project)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Проект с таким uuid не найден",
    )


async def delete_project_by_uuid(
    project_uuid: Annotated[UUID, Depends(validate_uuid_str)],
    user_id: Annotated[
        str,
        Depends(token_utils.strict_validate_access_token),
    ],
) -> bool:
    user = await crud_manager.user.get_one(
        field="id",
        value=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Возникла ошибка при получении пользователя",
        )

    project = await crud_manager.project.get_project_by_id(
        project_uuid=project_uuid,
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект с таким uuid не найден",
        )

    if project.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления проекта",
        )

    await crud_manager.project.delete("id", project.id)
    return True
