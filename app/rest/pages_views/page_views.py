from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from api.api_v2.users_views.projects_views.dependencies import (
    get_project_by_uuid,
    get_user_projects,
)
from core.config import settings
from core.database.schemas import ProjectResponseSchema
from paths_constants import templates
from schemas import ProjectReadSchema

from .dependencies import (
    get_dict_with_user_affirmations,
    return_data_for_user_profile_template,
    rmq_router,
)

router = APIRouter(
    tags=["Page views"],
)


@router.get(
    "/affirmations",
    include_in_schema=settings.run.dev_mode,
)
async def page_user_affirmations(
    affirmations: Annotated[
        dict[str, Any],
        Depends(get_dict_with_user_affirmations),
    ],
) -> HTMLResponse:
    """Страница с пользовательскими аффирмациями"""

    return templates.TemplateResponse(
        "pages/affirmations.html",
        affirmations,
    )


@router.get(
    "/profile",
    include_in_schema=settings.run.dev_mode,
)
async def page_profile(
    template_data: Annotated[
        dict[str, Any],
        Depends(return_data_for_user_profile_template),
    ],
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    return templates.TemplateResponse(
        "profiles/profile.html",
        template_data,
    )


@router.get(
    "/projects2/{project_uuid}",
    name="user-projects:detail",
    include_in_schema=settings.run.dev_mode,
)
async def get_list_projects(
    request: Request,
    project: Annotated[
        ProjectResponseSchema,
        Depends(get_project_by_uuid),
    ],
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    return templates.TemplateResponse(
        "project/details.html",
        context={
            "request": request,
            "project": project.model_dump(),
        },
    )


@router.get(
    "/projects2",
    name="user-projects:list",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_detail_project(
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
        "project/list.html",
        context=context,
    )


router.include_router(rmq_router)
