from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from api.api_v2.auth import token_utils
from core import settings
from core.crud import crud_manager
from core.database.schemas import ProjectResponseSchema
from core.database.security import schemas as ak_schemas

from .dependencies import (
    delete_project_by_uuid,
    get_project_by_uuid,
    get_user_projects_by_tg_id,
    get_user_projects_by_user_id,
    validate_uuid_str,
)

router = APIRouter()


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
        Depends(token_utils.strict_validate_access_token),
    ],
)
async def get_project_by_id(
    project: Annotated[
        ProjectResponseSchema,
        Depends(get_project_by_uuid),
    ],
) -> ProjectResponseSchema:
    return project


@router.delete(
    "/{project_id}",
    summary="Delete project by UUID and user owner ID",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(delete_project_by_uuid),
    ],
)
async def delete_project(
    project_uuid: Annotated[UUID, Depends(validate_uuid_str)],
) -> None:
    """
    Удаляет проект с указанным ID
    """
    return


@router.post(
    "/generate-key",
    response_model=ak_schemas.APIKeyCreateResponse,
)
async def generate_api_key(
    data: ak_schemas.APIKeyCreateRequest,
    user: Annotated[
        str | bool,
        Depends(token_utils.strict_validate_access_token),
    ],
) -> ak_schemas.APIKeyCreateResponse:
    project = await crud_manager.project.get_project_by_id(project_uuid=data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    raw_key, instance = await crud_manager.api_keys.create(
        project_id=project.id,
        temporary=data.temporary,
    )

    response_instance = ak_schemas.APIKeyCreateResponse(
        key=raw_key,
        key_prefix=instance.key_prefix,
        created_at=instance.created_at,
        project_id=project.uuid,
        expires_at=instance.expires_at,
    )

    return response_instance
