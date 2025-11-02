from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from paths_constants import templates

router = APIRouter()


@router.get(
    "/login",
    name="auth:login",
)
async def get_login_page(
    request: Request,
    redirect_url: str | None = Query(default=None),  # noqa: FAST002
) -> HTMLResponse:
    redirect_path = redirect_url or None
    return templates.TemplateResponse(
        "auth/telegram_widget.html",
        context={
            "request": request,
            "redirect_url": redirect_path,
        },
    )
