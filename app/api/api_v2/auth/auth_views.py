import logging
from typing import Annotated, Any
from urllib.parse import parse_qsl

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)

from app_exceptions import UserAlreadyExistsError
from core.config import settings
from core.crud import GetCRUDService
from paths_constants import templates
from schemas import UserCreateSchema

from . import access_token_helper, auth_utils

log = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/apps/{bot_name}",
    response_class=HTMLResponse,
    response_model=None,
)
async def handle_telegram_init(
    request: Request,
    bot_name: str,
    cookie_token: Annotated[
        str,
        Depends(access_token_helper.soft_validate_access_token),
    ],
) -> RedirectResponse | HTMLResponse:
    bot_config = access_token_helper.BOT_CONFIG.get(bot_name, {})

    if not cookie_token:
        errors = "" if bot_config else "Bot not found"
        return templates.TemplateResponse(
            "basebots.html",
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
async def auth_redirect() -> RedirectResponse:
    # Редирект на /auth/bot1 с нужным кодом
    return RedirectResponse(
        url="/auth/bot1",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@router.post("/auth/{bot_name}")
async def auth_user(
    request: Request,
    bot_name: str,
    data_validate: Annotated[
        dict[str, Any],
        Depends(auth_utils.verified_data_dependency),
    ],
    crud_service: GetCRUDService,
) -> RedirectResponse:
    client_type: str = data_validate["client_type"]
    access_validate: bool = data_validate["is_authorized"]

    log.info(
        "Auth request started | "
        "Path: %s | "
        "Client type: %s | "
        "Bot: %s | "
        "Access: %s",
        request.url.path,
        client_type,
        bot_name,
        access_validate,
    )

    bot_data = access_token_helper.BOT_CONFIG.get(bot_name, {})
    redirect_url = bot_data.get("redirect_url", "/profile")

    raw_data = (await request.body()).decode()
    data_dict = dict(
        parse_qsl(
            raw_data,
            keep_blank_values=True,
        ),
    )

    if client_type == "TelegramWidget":
        user_data = data_dict
    else:
        user_data = await auth_utils.extract_user_data(data_dict)
    user_data["tg_id"] = user_data.pop("id")
    try:
        user = await crud_service.user.create_user(
            user_create=UserCreateSchema.model_validate(user_data),
        )
    except UserAlreadyExistsError:
        user = await crud_service.user.get_by_tg_id(
            int(user_data["tg_id"]),
        )

    # Формирую ответ
    response = RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )

    # Генерирую токены
    jwt_token = await access_token_helper.sign_jwt_token(user.id)
    csrf_token = access_token_helper.sign_csrf_token()

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

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        secure=True,
        samesite="none",
        path="/",
        max_age=1800,
    )
    return response


@router.post("/refresh-csrf")
async def refresh_csrf(
    request: Request,
) -> JSONResponse:
    # Проверяю JWT токен
    token = request.cookies.get("jwt_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    await access_token_helper.decode_jwt(token)

    new_csrf_token = access_token_helper.sign_csrf_token()

    response = JSONResponse({"status": "CSRF token refreshed"})
    response.set_cookie(
        key="csrf_token",
        value=new_csrf_token,
        secure=True,
        samesite="lax",
        max_age=1800,
    )
    return response
