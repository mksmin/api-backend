from fastapi import APIRouter, Depends
from starlette import status

from api.api_v2.users_views.projects_views.dependencies import delete_project_by_uuid

router = APIRouter(
    prefix="/{project_uuid}",
)


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
