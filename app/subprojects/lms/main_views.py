from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from api.api_v2.users_views.projects_views.dependencies import get_user_projects
from paths_constants import templates
from rest.pages_views.redirect import redirect_to_login_page
from schemas import ProjectReadSchema

router = APIRouter()


@router.get(
    "/",
    name="lms:index-page",
    dependencies=[
        Depends(
            redirect_to_login_page,
        ),
    ],
)
async def get_index_lms_page(
    request: Request,
    projects: Annotated[
        list[ProjectReadSchema],
        Depends(
            get_user_projects,
        ),
    ],
) -> HTMLResponse:

    return templates.TemplateResponse(
        request=request,
        name="subprojects/lms/projects/list.html",
        context={
            "projects": projects,
            "can_create_projects": True,
        },
    )
