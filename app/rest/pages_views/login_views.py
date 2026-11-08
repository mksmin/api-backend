from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi_csrf_protect import CsrfProtect

from auth import jwt_helper
from auth.redirects import safe_login_redirect
from config import settings
from config.auth_bots import BotsEnum
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
        request=request,
        name="auth/telegram_widget.html",
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
        request=request,
        name="/auth/telegram_login_library.html",
        context={
            "request": request,
            "redirect_url": redirect_path,
            "client_id": settings.bots[BotsEnum.MININWORK_BOT].client_id,
        },
    )


@router.get(
    "/login/credentials",
    name="auth:credentials",
    response_model=None,
)
async def get_login_credentials_page(
    request: Request,
    cookie_token: Annotated[
        str,
        Depends(
            jwt_helper.soft_validate_access_token,
        ),
    ],
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
    redirect_url: Annotated[
        str | None,
        Query(),
    ] = None,
) -> HTMLResponse | RedirectResponse:
    redirect_path = safe_login_redirect(redirect_url)
    if cookie_token:
        return RedirectResponse(
            url=redirect_path,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name="/auth/login_credentials.html",
        context={
            "request": request,
            "csrf_token": csrf_token,
            "redirect_path": redirect_path,
        },
    )
    csrf_protect.set_csrf_cookie(
        signed_token,
        response,
    )
    return response
