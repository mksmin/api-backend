# import lib
from urllib.parse import parse_qsl

import aio_pika
import json
import pprint
import uuid

# import from lib
from fastapi import APIRouter, Depends, Request, HTTPException, Cookie, status, Query
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path


# import from modules
from app.core import settings, logger, crud_manager
from app.core.database import User
from .auth import auth_utils

router = APIRouter()
BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front") if settings.run.dev_mode else (BASE_DIR / "frontend")
)
HTML_DIR = FRONTEND_DIR / "src"
STATIC_DIR = FRONTEND_DIR / "public"
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")
not_found_404 = FRONTEND_DIR / "src/404.html"


async def get_current_user(search_field: str, value: str | int) -> User | None:
    """
    Получаю текущего пользователя из БД
    :return:
    """
    user = crud_manager.user.get_one()
    return user


async def check_path(path_file: Path):
    file_exists = Path(path_file).exists()

    if file_exists:
        return path_file, 200
    else:
        return not_found_404, 404


async def check_access_token(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> str | bool:
    """Middleware for checking access token from cookies"""
    if not access_token:
        return False

    try:
        payload = await auth_utils.decode_jwt(access_token)

        user_id: str = payload.get("user_id")
        logger.info(f"Check access token for user_id: {user_id}")
        if not user_id:
            return False
        return access_token

    except HTTPException as he:
        logger.error(f"Error in middleware: {he}", exc_info=True)
        return False


@router.get("/")
async def index_page():
    """
    Returns the index HTML file.

    Returns:
        FileResponse: The index HTML file.
    """
    index_html = HTML_DIR / "index.html"
    return FileResponse(index_html)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Returns the favicon ICO file.

    Returns:
        FileResponse: The favicon ICO file.
    """
    favicon_path = STATIC_DIR / "favicon.ico"
    return FileResponse(favicon_path)


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    """
    Returns the robots TXT file.

    Returns:
        FileResponse: The robots TXT file.
    """
    robots_path = STATIC_DIR / "robots.txt"
    return FileResponse(robots_path)


@router.get("/html/{name_html}", include_in_schema=False)
async def html_path(name_html: str):
    """
    Returns the specified HTML file.

    Args:
        name_html (str): The name of the HTML file.

    Returns:
        FileResponse: The specified HTML file.
    """
    html_file_path = HTML_DIR / name_html
    result, status = await check_path(html_file_path)
    return FileResponse(result, status_code=status)


#
@router.get("/media/{name_media}", include_in_schema=False)
async def html_path(name_media: str):
    """
    Returns the specified media file.

    Args:
        name_media (str): The name of the media file.

    Returns:
        FileResponse: The specified media file.
    """
    media_path = STATIC_DIR / "media" / name_media
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@router.get("/style/{name_style}", include_in_schema=False)
async def html_path(name_style: str):
    """
    Returns the specified style file.

    Args:
        name_style (str): The name of the style file.

    Returns:
        FileResponse: The specified style file.
    """
    media_path = HTML_DIR / "style" / name_style
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@router.get("/scripts/{name_script}", include_in_schema=False)
async def html_path(name_script: str):
    """
    Returns the specified script file.

    Args:
        name_script (str): The name of the script file.

    Returns:
        FileResponse: The specified script file.
    """
    script_path = HTML_DIR / "scripts" / name_script
    result, status = await check_path(script_path)
    return FileResponse(result, status_code=status)


@router.get("/affirmations", include_in_schema=False)
@router.get("/profile", include_in_schema=False)
async def user_profile_tg(request: Request):
    """Главная страница профиля"""
    # Определяем контент в зависимости от авторизации
    # content_template = "profile.html" if user else "auth_widget.html"
    content_template = "auth_widget.html"
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "content_template": content_template},
    )


async def get_affirmations_data(user_data: dict):
    try:
        rabbit_request = {
            "request": "GET",
            "endpoint": "/user/affirmations",
            "data": {
                "user_tg_id": int(user_data.get("id")),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "username": user_data.get("username", ""),
            },
        }
        correlation_id = str(uuid.uuid4())
        connection = await aio_pika.connect_robust(f"{settings.rabbit.url}")
        channel = await connection.channel()
        reply_queue = await channel.declare_queue(exclusive=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(rabbit_request).encode(),
                reply_to=reply_queue.name,
                correlation_id=correlation_id,
            ),
            routing_key="tasks",
        )
        # Ожидание ответа из временной очереди
        response = None
        try:
            async with reply_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        if message.correlation_id == correlation_id:
                            response = json.loads(message.body)
                            data_dict = {
                                "user": user_data,
                                "affirm": response.get("tasks", []),  # Пример данных
                            }
                            return data_dict

        finally:
            await connection.close()
            print("Соединение закрыто")
        # Проверка ответа и возврат шаблона
        if not response:
            raise HTTPException(500, "No response from /tasks")

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content")
async def get_content(request: Request, user: str | bool = Depends(check_access_token)):
    if not user:
        return JSONResponse(
            content={"status": "Unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED
        )

    path = request.query_params.get("page", "profile").lstrip("/")
    path_parts = path.split("/")
    if len(path_parts) == 1:
        page = path_parts[0]
    elif len(path_parts) == 2 and path_parts[0] == "apps":
        bot_name = auth_utils.BOT_CONFIG.get(path_parts[1], None)
        page = "profile" if not bot_name else bot_name["redirect_url"]
    else:
        page = "profile"

    content_template = f"{page}.html"

    logger.info(f"Получен запрос на страницу {page} из пути /content")

    payload = await auth_utils.decode_jwt(user)
    user_id: str = payload.get("user_id")
    user = await crud_manager.user.get_one(field="tg_id", value=int(user_id))

    if not user:
        return None

    user_data = {
        "id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    }

    if page == "/affirmations":
        print("page", page)
        data_dict = await get_affirmations_data(user_data)
        data_dict["request"] = request
        html_content = templates.TemplateResponse(content_template, data_dict)
        return html_content

    html_content = templates.TemplateResponse(
        content_template,
        {
            "request": request,
            "user": {
                "id": user_data.get("id"),
                "first_name": user_data.get("first_name", None),
                "last_name": user_data.get("last_name", None),
                "username": user_data.get("username", None),
                "is_premium": user_data.get("is_premium", None),
                "photo_url": user_data.get(
                    "photo_url",
                    "https://t.me/i/userpic/320/KAW0oZ7WjH_Mp1p43zuUi2lzp_IW2rxF954-zq5f3us.jpg",
                ),
                "language_code": user_data.get("language_code", "ru"),
                "allows_write_to_pm": user_data.get("allows_write_to_pm", None),
            },
        },
    )
    return html_content


@router.get("/apps/{bot_name}", response_class=HTMLResponse)
async def handle_telegram_init(request: Request, bot_name: str):
    # Проверяем существование бота
    bot_config = auth_utils.BOT_CONFIG.get(bot_name)
    if not bot_config:
        raise HTTPException(404, detail="Bot not found")

    return templates.TemplateResponse(
        "basebots.html",
        {"request": request},
    )


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

    logger.debug(f"Received data (id): {data_dict.get('id')}")

    if client_type == "TelegramWidget":
        user_id = data_dict.get("id")
        logger.debug(f"TelegramWidget, user_id: {user_id}")
    else:
        user_data = await auth_utils.extract_user_data(data_dict)
        user_id = user_data.get("id")
        logger.debug(f"Extracted user data: {user_data.keys()}")

    # Формирую ответ
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    # Генерирую токены
    logger.debug(f"Generating tokens for user {user_id}")
    jwt_token = await auth_utils.sign_jwt_token(int(user_id))
    csrf_token = await auth_utils.sign_csrf_token()

    logger.info(
        f"Tokens generated | User: {user_id} | "
        f"JWT expiry: {auth_utils.ACCESS_TOKEN_EXPIRE_HOURS}h"
    )

    # Устанавливаю куки
    response.set_cookie(
        key="access_token",
        value=jwt_token["access_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=auth_utils.ACCESS_TOKEN_EXPIRE_HOURS * 900,
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
        await auth_utils.decode_jwt(token)

    except HTTPException as he:
        raise he

    new_csrf_token = await auth_utils.sign_csrf_token()

    response = JSONResponse({"status": "CSRF token refreshed"})
    response.set_cookie(
        key="csrf_token",
        value=new_csrf_token,
        secure=True,
        samesite="lax",
        max_age=1800,
    )
    return response


@router.post("/verify-widget-tg")
async def verify_telegram(
    request: Request,
    pairs: list = auth_utils.get_verified_data("atombot"),
):
    data_dict = dict(pairs)
    user_data = {"user": json.dumps(data_dict)}

    # print(f"user_data: {user_data}")

    user_data = await auth_utils.extract_user_data(user_data)
    data_dict = {"request": request, "user": user_data}

    return await auth_utils.process_profile("profile.html", data_dict)


@router.post("/verify-widget-tg-affirm")
async def verify_telegram(
    request: Request,
    pairs: list = auth_utils.get_verified_data("atombot"),
):
    data_dict = dict(pairs)
    user_data = {"user": json.dumps(data_dict)}

    # print(f"user_data: {user_data}")

    try:
        user_data = await auth_utils.extract_user_data(dict(user_data))

        rabbit_request = {
            "request": "GET",
            "endpoint": "/user/affirmations",
            "data": {
                "user_tg_id": int(user_data.get("id")),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "username": user_data.get("username", ""),
            },
        }

        correlation_id = str(uuid.uuid4())
        connection = await aio_pika.connect_robust(f"{settings.rabbit.url}")
        channel = await connection.channel()
        reply_queue = await channel.declare_queue(exclusive=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(rabbit_request).encode(),
                reply_to=reply_queue.name,
                correlation_id=correlation_id,
            ),
            routing_key="tasks",
        )
        # Ожидание ответа из временной очереди
        response = None
        try:
            async with reply_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        if message.correlation_id == correlation_id:
                            response = json.loads(message.body)
                            data_dict = {
                                "request": request,
                                "user": user_data,
                                "affirm": response.get("tasks", []),  # Пример данных
                            }
                            return await auth_utils.process_profile(
                                "affirm.html", data_dict
                            )

        finally:
            await connection.close()
            print("Соединение закрыто")
        # Проверка ответа и возврат шаблона
        if not response:
            raise HTTPException(500, "No response from /tasks")

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-tg")
async def verify_telegram(
    request: Request,
    pairs: list = auth_utils.get_verified_data("testbot"),
):
    data_dict = dict(pairs)
    user_data = await auth_utils.extract_user_data(data_dict)
    data_dict = {"request": request, "user": user_data}

    return await auth_utils.process_profile("profile.html", data_dict)


@router.post("/verify-affirm")
async def verify_affirm(
    request: Request,
    pairs: list = auth_utils.get_verified_data("mininbot"),
):
    try:
        user_data = await auth_utils.extract_user_data(dict(pairs))

        rabbit_request = {
            "request": "GET",
            "endpoint": "/user/affirmations",
            "data": {
                "user_tg_id": int(user_data.get("id")),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "username": user_data.get("username", ""),
            },
        }

        correlation_id = str(uuid.uuid4())
        connection = await aio_pika.connect_robust(f"{settings.rabbit.url}")
        channel = await connection.channel()
        reply_queue = await channel.declare_queue(exclusive=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(rabbit_request).encode(),
                reply_to=reply_queue.name,
                correlation_id=correlation_id,
            ),
            routing_key="tasks",
        )
        # Ожидание ответа из временной очереди
        response = None
        try:
            async with reply_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        if message.correlation_id == correlation_id:
                            response = json.loads(message.body)
                            data_dict = {
                                "request": request,
                                "user": user_data,
                                "affirm": response.get("tasks", []),  # Пример данных
                            }
                            return await auth_utils.process_profile(
                                "affirm.html", data_dict
                            )

        finally:
            await connection.close()
            print("Соединение закрыто")
        # Проверка ответа и возврат шаблона
        if not response:
            raise HTTPException(500, "No response from /tasks")

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
