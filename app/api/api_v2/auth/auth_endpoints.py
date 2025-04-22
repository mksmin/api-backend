# import from lib
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from pathlib import Path
from urllib.parse import parse_qsl

# import from modules
from . import auth_utils, token_utils
from app.core import logger, settings, crud_manager
from app.core.database import User

router = APIRouter()
BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front") if settings.run.dev_mode else (BASE_DIR / "frontend")
)
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")


@router.get("/apps/{bot_name}", response_class=HTMLResponse)
async def handle_telegram_init(
    request: Request,
    bot_name: str,
    cookie_token: str = Depends(token_utils.check_access_token),
):
    if not cookie_token:
        # Проверяем существование бота
        bot_config = auth_utils.BOT_CONFIG.get(bot_name)
        if not bot_config:
            raise HTTPException(404, detail="Bot not found")

        return templates.TemplateResponse(
            "basebots.html",
            {"request": request},
        )

    bot_data = auth_utils.BOT_CONFIG.get(bot_name)
    redirect_url = bot_data.get("redirect_url", "/profile")
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    return response


@router.post("/auth")
async def auth_redirect():
    # Редирект на /auth/bot1 с нужным кодом
    return RedirectResponse(
        url="/auth/bot1", status_code=status.HTTP_308_PERMANENT_REDIRECT
    )


@router.post("/auth/{bot_name}")
async def auth_user(
    request: Request,
    bot_name: str | None = Path(default=None),
    data_validate: dict = Depends(auth_utils.verified_data_dependency),
):
    client_type: str = data_validate.get("client_type")
    access_validate: bool = data_validate.get("is_authorized")

    logger.info(
        "Auth request started | "
        f"Path: {request.url.path} | "
        f"Client type: {client_type} | "
        f"Bot: {bot_name} | "
        f"Access: {access_validate}"
    )

    bot_data = auth_utils.BOT_CONFIG.get(bot_name)
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
    csrf_token = await token_utils.sign_csrf_token()

    logger.info(
        f"Tokens generated | User: {user.id} | "
        f"JWT expiry: {settings.access_token.lifetime_seconds}s"
    )

    # Устанавливаю куки
    response.set_cookie(
        key="access_token",
        value=jwt_token["access_token"],
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
async def refresh_csrf(request: Request):
    # Проверяю JWT токен
    token = request.cookies.get("jwt_token")
    if not token:
        raise HTTPException(401, "Unauthorized")

    try:
        await token_utils.decode_jwt(token)

    except HTTPException as he:
        raise he

    new_csrf_token = await token_utils.sign_csrf_token()

    response = JSONResponse({"status": "CSRF token refreshed"})
    response.set_cookie(
        key="csrf_token",
        value=new_csrf_token,
        secure=True,
        samesite="lax",
        max_age=1800,
    )
    return response
