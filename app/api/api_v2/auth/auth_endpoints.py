from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core import logger, settings
from core.crud import crud_manager

if TYPE_CHECKING:
    from core.database import User


from . import auth_utils, token_utils

router = APIRouter()

BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front")
    if settings.run.dev_mode
    else (BASE_DIR.parent / "frontend")
)
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")


@router.get(
    "/apps/{bot_name}",
    response_class=HTMLResponse,
    response_model=None,
)
async def handle_telegram_init(
    request: Request,
    bot_name: str,
    cookie_token: Annotated[str, Depends(token_utils.soft_validate_access_token)],
) -> RedirectResponse | HTMLResponse:
    if not cookie_token:
        # Проверяем существование бота
        bot_config = token_utils.BOT_CONFIG.get(bot_name)
        if not bot_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot not found",
            )

        return templates.TemplateResponse(
            "basebots.html",
            {"request": request},
        )

    bot_data = token_utils.BOT_CONFIG.get(bot_name, {})
    redirect_url = bot_data.get("redirect_url", "/profile")
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


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
) -> RedirectResponse:
    client_type: str = data_validate["client_type"]
    access_validate: bool = data_validate["is_authorized"]

    logger.info(
        "Auth request started | "
        f"Path: {request.url.path} | "
        f"Client type: {client_type} | "
        f"Bot: {bot_name} | "
        f"Access: {access_validate}",
    )

    bot_data = token_utils.BOT_CONFIG.get(bot_name, {})
    redirect_url = bot_data.get("redirect_url", "/profile")
    logger.debug(f"Redirect URL: {redirect_url}")

    raw_data = await request.body()
    raw_data_str = raw_data.decode()
    pairs = parse_qsl(raw_data_str, keep_blank_values=True)
    data_dict = dict(pairs)

    logger.debug(f"Received data (id): {data_dict}")

    if client_type == "TelegramWidget":
        user_data = data_dict
    else:
        user_data = await auth_utils.extract_user_data(data_dict)
    user_data["tg_id"] = user_data.pop("id")
    logger.debug(f"User data: {user_data}")

    user: User = await crud_manager.user.create(data=user_data)
    logger.debug(f"User data saved: {user.id = }")

    # Формирую ответ
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    # Генерирую токены
    logger.debug(f"Generating tokens for user {user.id}")
    jwt_token = await token_utils.sign_jwt_token(int(user.id))
    csrf_token = token_utils.sign_csrf_token()

    logger.info(
        f"Tokens generated | User: {user.id} | "
        f"JWT expiry: {settings.access_token.lifetime_seconds}s",
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

    await token_utils.decode_jwt(token)

    new_csrf_token = token_utils.sign_csrf_token()

    response = JSONResponse({"status": "CSRF token refreshed"})
    response.set_cookie(
        key="csrf_token",
        value=new_csrf_token,
        secure=True,
        samesite="lax",
        max_age=1800,
    )
    return response
