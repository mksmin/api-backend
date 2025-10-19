from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from api.api_v2.auth import token_utils
from core.crud import crud_manager
from core.database.schemas import ProjectRequestSchema, ProjectResponseSchema
from core.database.security import schemas as ak_schemas

router = APIRouter()


@router.post(
    "/",
    dependencies=[
        Depends(token_utils.strict_validate_access_token),
    ],
)
async def create_project(
    project_create: ProjectRequestSchema,
) -> ProjectResponseSchema:
    project = await crud_manager.project.create(
        project_create.model_dump(),
    )
    return ProjectResponseSchema.model_validate(project)


@router.post(
    "/generate-key",
    response_model=ak_schemas.APIKeyCreateResponse,
    dependencies=[
        Depends(token_utils.strict_validate_access_token),
    ],
)
async def generate_api_key(
    data: ak_schemas.APIKeyCreateRequest,
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

    return ak_schemas.APIKeyCreateResponse(
        key=raw_key,
        key_prefix=instance.key_prefix,
        created_at=instance.created_at,
        project_id=project.uuid,
        expires_at=instance.expires_at,
    )
