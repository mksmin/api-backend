from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from api.api_v2.users_views.projects_views.dependencies import get_user_projects
from auth import jwt_helper
from config import settings
from paths_constants import templates
from schemas import ProjectReadSchema

router = APIRouter()


@router.get(
    "/",
    name="lms:index-page",
)
async def get_index_lms_page(
    request: Request,
    projects: Annotated[
        list[ProjectReadSchema],
        Depends(
            get_user_projects,
        ),
    ],
    user_id: Annotated[
        str,
        Depends(jwt_helper.soft_validate_access_token),
    ],
) -> HTMLResponse:

    return templates.TemplateResponse(
        request=request,
        name="subprojects/lms/projects/list.html",
        context={
            "projects": projects,
            "can_create_projects": settings.lms.can_create_project(
                int(user_id),
            ),
        },
    )
