from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse

from api.api_v2.users_views.projects_views.dependencies import get_project_by_uuid
from config import settings
from paths_constants import templates
from schemas import ProjectReadSchema
from subprojects.lms.constraints import LMS_TEMPLATE_PATH

router = APIRouter()


@router.get(
    "/{project_uuid}",
    name="lms-project:detail",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_project_detail(
    request: Request,
    project: Annotated[
        ProjectReadSchema | None,
        Depends(get_project_by_uuid),
    ],
) -> HTMLResponse:
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return templates.TemplateResponse(
        request=request,
        name=f"{LMS_TEMPLATE_PATH}/projects/details.html",
        context={
            "request": request,
            "project": project.model_dump(),
        },
    )
