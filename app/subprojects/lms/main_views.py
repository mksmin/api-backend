from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from paths_constants import templates
from rest.pages_views.redirect import redirect_to_login_page

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
) -> HTMLResponse:
    projects = [
        {
            "id": 1,
            "name": "Атом-лаб 2026",
            "role": "Владелец",
            "stream_count": 3,
            "participant_count": 124,
        },
        {
            "id": 2,
            "name": "Школа наставников",
            "role": "Администратор",
            "stream_count": 2,
            "participant_count": 48,
        },
        {
            "id": 3,
            "name": "ИТ-интенсив",
            "role": "Куратор",
            "stream_count": 1,
            "participant_count": 32,
        },
    ]
    return templates.TemplateResponse(
        request=request,
        name="subprojects/lms/projects/list.html",
        context={
            "projects": projects,
            "can_create_projects": True,
        },
    )
