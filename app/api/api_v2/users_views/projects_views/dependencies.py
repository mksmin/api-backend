from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.api_v2.auth import token_utils
from core.crud import crud_manager
from core.database.schemas import ProjectResponseSchema

from .schemas import ProjectFilter


async def validate_uuid_str(project_uuid: str) -> UUID:
    try:
        return UUID(project_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректный формат UUID",
        )


async def get_user_projects_by_tg_id(
    prj_filter: Annotated[
        ProjectFilter,
        Depends(ProjectFilter.from_query),
    ],
) -> dict[int, ProjectResponseSchema]:
    try:
        user = await crud_manager.user.get_one(value=prj_filter.owner_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        projects = await crud_manager.project.get_all(user.id)

        return {
            i: ProjectResponseSchema.model_validate(project)
            for i, project in enumerate(projects)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": str(e),
            },
        )


async def get_user_projects_by_user_id(
    user_id: str = Depends(token_utils.strict_validate_access_token),
) -> dict[int, ProjectResponseSchema]:
    projects = await crud_manager.project.get_all(int(user_id))
    return {
        i: ProjectResponseSchema.model_validate(project)
        for i, project in enumerate(projects)
    }


async def get_project_by_uuid(
    project_uuid: UUID = Depends(validate_uuid_str),
) -> ProjectResponseSchema:
    if project := await crud_manager.project.get_project_by_id(
        project_uuid=project_uuid,
    ):
        return ProjectResponseSchema.model_validate(project)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект с таким uuid не найден",
        )


async def delete_project_by_uuid(
    project_uuid: UUID = Depends(validate_uuid_str),
    user_id: str = Depends(token_utils.strict_validate_access_token),
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

    if project.prj_owner != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления проекта",
        )

    await crud_manager.project.delete("id", project.id)
    return True
