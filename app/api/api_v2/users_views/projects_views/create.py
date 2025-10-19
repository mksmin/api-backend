from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from api.api_v2.auth import token_utils
from app_exceptions import InvalidUUIDError, UserNotFoundError
from app_exceptions.exceptions import ProjectAlreadyExistsError
from core.crud import crud_manager
from core.crud.crud_service import GetCRUDService
from core.database.security import schemas as ak_schemas
from schemas import ProjectCreateSchema, ProjectReadSchema

router = APIRouter()


@router.post(
    "/",
)
async def create_project(
    crud_service: GetCRUDService,
    project_create: ProjectCreateSchema,
    user_id: Annotated[
        str,
        Depends(token_utils.strict_validate_access_token),
    ],
) -> ProjectReadSchema:
    try:
        result = await crud_service.project.create_project(
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
    else:
        return result


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
