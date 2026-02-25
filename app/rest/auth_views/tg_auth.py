import json
import logging
from typing import Annotated
from typing import Any
from urllib.parse import parse_qsl

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

from app_exceptions import UserAlreadyExistsError
from auth import jwt_helper
from auth import tg_auth_depends
from auth.tg_auth_depends import verify_client
from config import settings
from core.crud import GetCRUDService
from paths_constants import templates
from schemas import UserCreateSchema

log = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/apps/{bot_name}",
    response_class=HTMLResponse,
    response_model=None,
)
async def tg_mini_app_page(
    request: Request,
    bot_name: str,
    cookie_token: Annotated[
        str,
        Depends(jwt_helper.soft_validate_access_token),
    ],
) -> RedirectResponse | HTMLResponse:
    bot_config = jwt_helper.BOT_CONFIG.get(bot_name, {})

    if not cookie_token:
        errors = "" if bot_config else "Bot not found"
        return templates.TemplateResponse(
            "/auth/telegram_miniapp.html",
            {
                "request": request,
                "botConfigPath": bot_config.get("name"),
                "errors": errors,
            },
        )

    redirect_url = bot_config.get("redirect_url", "/profile")
    return RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/auth")
async def auth_redirect(
    request: Request,
) -> RedirectResponse:
    return RedirectResponse(
        url=request.url_for(
            "auth_bots",
            bot_name="bot1",
        ),
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@router.post(
    "/auth/{bot_name}",
    name="auth_bots",
)
async def auth_user_via_tg_bot(
    request: Request,
    bot_name: str,
    client_type: Annotated[str, Depends(verify_client)],
    data_validate: Annotated[
        dict[str, Any],
        Depends(tg_auth_depends.verified_tg_data_dependency),
    ],
    crud_service: GetCRUDService,
) -> JSONResponse:

    log.info(
        "Auth request started | "
        "Path: %s | "
        "Client type: %s | "
        "Bot: %s | "
        "Access: %s",
        request.url.path,
        client_type,
        bot_name,
        data_validate,
    )

    bot_data = jwt_helper.BOT_CONFIG.get(bot_name, {})
    redirect_url = bot_data.get("redirect_url", "/profile")

    raw_data = (await request.body()).decode()
    data_dict = dict(
        parse_qsl(
            raw_data,
            keep_blank_values=True,
        ),
    )

    if client_type == "TelegramWidget":
        user_data = json.loads(raw_data)
    else:
        user_data = await tg_auth_depends.extract_user_data(data_dict)
    user_data["tg_id"] = user_data.pop("id")
    try:
        user = await crud_service.user.create_user(
            user_create=UserCreateSchema.model_validate(user_data),
        )
    except UserAlreadyExistsError:
        user = await crud_service.user.get_by_tg_id(
            int(user_data["tg_id"]),
        )

    response = JSONResponse(
        {"redirect_url": redirect_url},
        status_code=status.HTTP_200_OK,
    )

    jwt_token = await jwt_helper.sign_jwt_token(user.id)

    log.info(
        "Tokens generated | User: %d | JWT expiry: %d",
        user.id,
        settings.access_token.lifetime_seconds,
    )

    # Устанавливаю куки
    response.set_cookie(
        key="access_token",
        value=str(jwt_token["access_token"]),
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=settings.access_token.lifetime_seconds,
    )
    return response
