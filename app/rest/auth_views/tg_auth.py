import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

from auth import jwt_helper
from auth.dependencies import AuthUserViaTgMiniapp
from auth.dependencies import AuthUserViaTgWidget
from config import settings
from config.auth_bots import BotsEnum
from paths_constants import templates

log = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/apps/{bot_name}",
    response_class=HTMLResponse,
    response_model=None,
)
async def tg_mini_app_page(
    request: Request,
    bot_name: Annotated[
        str,
        Path(),
    ],
    cookie_token: Annotated[
        str,
        Depends(jwt_helper.soft_validate_access_token),
    ],
) -> RedirectResponse | HTMLResponse:
    template_path = "/auth/telegram_miniapp.html"
    ctx: dict[str, str | Request] = {}
    ctx.update(
        request=request,
        bot_name="",
        bot_auth_path="",
        errors="",
    )
    try:
        bot_enum = BotsEnum(bot_name)
    except ValueError:
        errors = "Unknown authenticating bot"
        ctx.update(
            errors=errors,
        )
        return templates.TemplateResponse(
            template_path,
            ctx,
        )

    if not cookie_token:
        auth_path = request.url_for(
            "auth_tg_miniapp",
            bot_name=bot_enum,
        ).path
        ctx.update(
            botName=bot_enum,
            bot_auth_path=auth_path,
        )
        return templates.TemplateResponse(
            template_path,
            ctx,
        )
    return RedirectResponse(
        url=settings.bots[bot_enum].redirect_path,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/auth/tg/miniapp/{bot_name}",  # noqa: FAST003
    name="auth_tg_miniapp",
)
async def auth_tg_miniapp(
    response: AuthUserViaTgMiniapp,
) -> JSONResponse:
    return response


@router.post(
    "/auth/tg/widget/{bot_name}",  # noqa: FAST003
    name="auth_tg_widget",
)
async def auth_tg_widget(
    response: AuthUserViaTgWidget,
) -> JSONResponse:
    return response


#
#
# @router.post(
#     "/auth/max/miniapp/{bot_name}",
#     name="auth_max_miniapp",
# )
# async def auth_max_miniapp(
#     response: JSONResponse,
# ) -> JSONResponse:
#     return response


# @router.post("/auth")
# async def auth_redirect(
#     request: Request,
# ) -> RedirectResponse:
#     return RedirectResponse(
#         url=request.url_for(
#             "auth_bots",
#             bot_name="bot1",
#         ),
#         status_code=status.HTTP_308_PERMANENT_REDIRECT,
#     )
