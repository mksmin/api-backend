from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Body,
    Header,
    Request,
    status,
)
from fastapi.responses import RedirectResponse

from core.config import settings

router = APIRouter(
    tags=["Redirects"],
)

actual_version = "/api/v2/"

path_mapping = {
    "users": actual_version + "users/",
}


@router.get(
    "/statistics/",
    include_in_schema=settings.run.dev_mode,
)
async def get_statistics(
    token: Annotated[str, Header()],  # noqa: ARG001
) -> RedirectResponse:
    return RedirectResponse(
        url=f"{path_mapping['users']}statistics",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@router.post(
    "/registration",
    include_in_schema=settings.run.dev_mode,
)
async def registration(
    data: Annotated[dict[str, Any], Body()],  # noqa: ARG001
) -> RedirectResponse:
    return RedirectResponse(
        url=f"{path_mapping['users']}registration",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@router.api_route(
    "/projects",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=settings.run.dev_mode,
)
async def project_redirect(
    request: Request,
) -> RedirectResponse:
    path = f"{path_mapping['users']}projects"
    if request.query_params:
        path = f"{path_mapping['users']}projects?{request.query_params}"
    return RedirectResponse(
        url=path,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.api_route(
    "/projects/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=settings.run.dev_mode,
)
async def project_nested_redirect(
    request: Request,
    path: str,
) -> RedirectResponse:
    query = f"?{request.query_params}" if request.query_params else ""
    return RedirectResponse(
        url=f"{path_mapping['users']}projects/{path}{query}",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.delete(
    "/projects/{project_id}",
    include_in_schema=settings.run.dev_mode,
)
async def create_project(
    project_id: int,
) -> RedirectResponse:
    return RedirectResponse(
        url=f"{path_mapping['users']}projects/{project_id}",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@router.post(
    "/tasks",
    include_in_schema=settings.run.dev_mode,
)
async def rabbit_task_create(
    data: Annotated[dict[str, Any], Body()],  # noqa: ARG001
) -> RedirectResponse:
    return RedirectResponse(
        url=f"{path_mapping['users']}tasks",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )
