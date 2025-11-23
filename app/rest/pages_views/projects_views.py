from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from api.api_v2.users_views.projects_views.dependencies import (
    get_project_by_uuid,
    get_user_projects,
)
from core.config import settings
from core.database.schemas import ProjectResponseSchema
from paths_constants import templates
from rest.pages_views.dependencies.user_data import (
    return_data_for_user_profile_template,
)
from rest.pages_views.redirect import redirect_to_login_page
from schemas import ProjectReadSchema

router = APIRouter(
    dependencies=[
        Depends(redirect_to_login_page),
    ],
)


@router.get(
    "/projects",
    name="user-projects:list",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_list_projects(
    request: Request,
    projects: Annotated[
        list[ProjectReadSchema],
        Depends(get_user_projects),
    ],
    template_data: Annotated[
        dict[str, Any],
        Depends(return_data_for_user_profile_template),
    ],
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    context = {
        "request": request,
        "projects": projects,
        "user": template_data.get("user"),
    }
    return templates.TemplateResponse(
        "projects/list.html",
        context=context,
    )


@router.get(
    "/projects/{project_uuid}",
    name="user-projects:detail",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_project_detail(
    request: Request,
    project: Annotated[
        ProjectResponseSchema,
        Depends(get_project_by_uuid),
    ],
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    return templates.TemplateResponse(
        "projects/details.html",
        context={
            "request": request,
            "project": project.model_dump() if project else None,
        },
    )
