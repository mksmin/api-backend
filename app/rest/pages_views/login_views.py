from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from auth import jwt_helper
from config import settings
from paths_constants import templates

router = APIRouter()


@router.get(
    "/login",
    name="auth:login",
    response_model=None,
)
async def get_login_page(
    request: Request,
    cookie_token: Annotated[
        str,
        Depends(jwt_helper.soft_validate_access_token),
    ],
    redirect_url: str | None = Query(default=None),  # noqa: FAST002
) -> HTMLResponse | RedirectResponse:

    if cookie_token:
        return RedirectResponse(
            url="/profile",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    redirect_path = redirect_url or None
    return templates.TemplateResponse(
        "auth/telegram_widget.html",
        context={
            "request": request,
            "redirect_url": redirect_path,
            "telegram_bot_id": settings.tg.widget_bot_id,
        },
    )


@router.get(
    "/login/new",
    name="auth:oidc_login",
    response_model=None,
)
async def get_oidc_login_page(
    request: Request,
    cookie_token: Annotated[
        str,
        Depends(jwt_helper.soft_validate_access_token),
    ],
    redirect_url: str | None = Query(default=None),  # noqa: FAST002
) -> HTMLResponse | RedirectResponse:

    if cookie_token:
        return RedirectResponse(
            url="/profile",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    redirect_path = redirect_url or None
    return templates.TemplateResponse(
        "/auth/telegram_login_library.html",
        context={
            "request": request,
            "redirect_url": redirect_path,
            "client_id": 6529338226,
        },
    )
