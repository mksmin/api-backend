from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from api.api_v2.auth import access_token_helper
from api.api_v2.users_views.projects_views.dependencies import (
    get_project_by_uuid,
    get_user_projects_by_tg_id,
    get_user_projects_by_user_id,
)
from core.config import settings
from core.database.schemas import ProjectResponseSchema

router = APIRouter()


@router.get(
    "/owner",
    summary="Get projects by owner",
    include_in_schema=settings.run.dev_mode,
    status_code=status.HTTP_200_OK,
)
async def get_projects_owner(
    projects: Annotated[
        dict[int, ProjectResponseSchema],
        Depends(get_user_projects_by_user_id),
    ],
) -> dict[int, ProjectResponseSchema]:
    """
    Возвращает список проектов, принадлежащих указанному пользователю.
    """
    return projects


@router.get(
    "/{project_uuid}",
    include_in_schema=settings.run.dev_mode,
    dependencies=[
        Depends(access_token_helper.strict_validate_access_token),
    ],
)
async def get_project(
    project: Annotated[
        ProjectResponseSchema,
        Depends(get_project_by_uuid),
    ],
) -> ProjectResponseSchema:
    return project


@router.get(
    "/",
    include_in_schema=settings.run.dev_mode,
)
async def get_projects(
    user_projects: Annotated[
        dict[int, ProjectResponseSchema],
        Depends(get_user_projects_by_tg_id),
    ],
) -> dict[int, ProjectResponseSchema]:
    return user_projects
