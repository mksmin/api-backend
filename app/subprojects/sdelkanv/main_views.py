from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from paths_constants import templates

router = APIRouter(
    prefix="/sdelkanv",
    tags=["Subprj Sdelkanv"],
    responses={
        404: {"description": "Not found"},
    },
)
templates_path = "subprojects/sdelkanv/"


@router.get(
    "/",
    name="sdelkanv:subscribe_page",
)
async def index_page(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        templates_path + "subscribe.html",
        context={
            "request": request,
            "redirect_url": "/test",
            "telegram_bot_id": "123",
        },
    )
