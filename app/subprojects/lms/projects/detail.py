from typing import Annotated

from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse

from auth import jwt_helper
from config import settings
from core.crud import GetCRUDService
from paths_constants import templates
from subprojects.lms.constraints import LMS_TEMPLATE_PATH
from subprojects.lms.projects.flows.list import OwnedProject

router = APIRouter()


@router.get(
    "/{project_uuid}",
    name="lms-project:detail",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_project_detail(
    request: Request,
    project: OwnedProject,
    crud_service: GetCRUDService,
    user_id: Annotated[
        str,
        Depends(
            jwt_helper.strict_validate_access_token,
        ),
    ],
) -> HTMLResponse:
    flows_count = await crud_service.lms_flow.count_by_project(
        project_id=project.id,
        user_id=int(user_id),
    )

    return templates.TemplateResponse(
        request=request,
        name=f"{LMS_TEMPLATE_PATH}/projects/details.html",
        context={
            "request": request,
            "project": project,
            "flows_count": flows_count,
            "project_section": "overview",
        },
    )
