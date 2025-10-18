from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from api.api_v2.auth import access_token_helper
from api.api_v2.users_views.projects_views.dependencies import (
    delete_project_by_uuid,
    get_project_by_uuid,
)
from core.config import settings
from core.database.schemas import ProjectResponseSchema

router = APIRouter(
    prefix="/{project_uuid}",
)


@router.get(
    "/",
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


@router.delete(
    "/",
    summary="Delete project by UUID and user owner ID",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(delete_project_by_uuid),
    ],
)
async def delete_project() -> None:
    """
    Удаляет проект с указанным ID
    """
    return
