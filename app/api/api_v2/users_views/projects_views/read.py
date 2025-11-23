from typing import Annotated

from fastapi import APIRouter, Depends

from api.api_v2.users_views.projects_views.dependencies import (
    get_project_by_uuid,
    get_user_projects,
)
from core.config import settings
from core.database.schemas import ProjectResponseSchema
from schemas import ProjectReadSchema

router = APIRouter()


@router.get(
    "/{project_uuid}",
    include_in_schema=settings.run.dev_mode,
)
async def get_project(
    project: Annotated[
        ProjectResponseSchema,
        Depends(get_project_by_uuid),
    ],
) -> ProjectResponseSchema | dict[str, str]:
    return project if project else {}


@router.get(
    "/",
    include_in_schema=settings.run.dev_mode,
)
async def get_projects(
    user_projects: Annotated[
        list[ProjectReadSchema],
        Depends(get_user_projects),
    ],
) -> list[ProjectReadSchema]:
    return user_projects
