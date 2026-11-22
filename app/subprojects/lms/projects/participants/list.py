from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from paths_constants import templates
from subprojects.lms.constraints import PARTICIPANTS_TEMPLATE_PATH
from subprojects.lms.projects.flows.list import OwnedProject

router = APIRouter()


@router.get(
    "/",
    name="lms-participants:list",
)
async def get_participants_list_page(
    request: Request,
    project: OwnedProject,
) -> HTMLResponse:

    context = {
        "project_section": "participants",
        "project": project,
        "enrollments": [
            {
                "uuid": "test-user-uuid",
                "full_name": "Testov Testovich",
                "email": "testov@example.com",
                "flow_uuid": "uuid-test",
                "flow_title": "Тестовый поток",
                "status": "active",
            },
        ],
        "can_manage_participants": True,
    }

    return templates.TemplateResponse(
        request=request,
        name=f"{PARTICIPANTS_TEMPLATE_PATH}/list.html",
        context=context,
    )
