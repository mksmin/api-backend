# import lib
import aio_pika
import json
import uuid

# import from lib
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path


# import from modules
from app.core import settings, logger, crud_manager
from app.core.database import User
from .auth import auth_utils, token_utils, auth_router

router = APIRouter()
router.include_router(
    auth_router,
)

BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front") if settings.run.dev_mode else (BASE_DIR / "frontend")
)
HTML_DIR = FRONTEND_DIR / "src"
STATIC_DIR = FRONTEND_DIR / "public"
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")
not_found_404 = FRONTEND_DIR / "src/404.html"


async def check_path(path_file: Path):
    file_exists = Path(path_file).exists()

    if file_exists:
        return path_file, 200
    else:
        return not_found_404, 404


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


@router.get("/robots.txt", include_in_schema=settings.run.dev_mode)
async def robots():
    """
    Returns the robots TXT file.

    Returns:
        FileResponse: The robots TXT file.
    """
    robots_path = STATIC_DIR / "robots.txt"
    return FileResponse(robots_path)


@router.get("/html/{name_html}", include_in_schema=settings.run.dev_mode)
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
@router.get("/media/{name_media}", include_in_schema=settings.run.dev_mode)
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


@router.get("/style/{name_style}", include_in_schema=settings.run.dev_mode)
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


@router.get("/scripts/{name_script}", include_in_schema=settings.run.dev_mode)
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


@router.get("/profile", include_in_schema=settings.run.dev_mode)
async def user_profile(
    request: Request, cookie_token: str = Depends(token_utils.check_access_token)
):
    """Главная страница профиля"""
    data_return = {
        "request": request,
        "auth_widget": None,
        "user": True,
    }

    if not cookie_token:
        # Определяем контент в зависимости от авторизации
        data_return = {
            "request": request,
            "auth_widget": "auth_widget.html",
            "user": None,
        }
        html_content = templates.TemplateResponse(
            "profiles/profile.html",
            data_return,
        )
        return html_content

    payload = await token_utils.decode_jwt(cookie_token)
    user_id: int = int(payload.get("user_id"))
    user: User = await crud_manager.user.get_one(field="id", value=user_id)

    user_data = {
        "id": user.tg_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "is_premium": True,
        "photo_url": "https://t.me/i/userpic/320/KAW0oZ7WjH_Mp1p43zuUi2lzp_IW2rxF954-zq5f3us.jpg",
        "language_code": "ru",
        "allows_write_to_pm": True,
    }

    data_return["user"] = user_data
    html_content = templates.TemplateResponse(
        "profiles/profile.html",
        data_return,
    )
    return html_content


@router.get("/affirmations", include_in_schema=settings.run.dev_mode)
async def page_user_affirmations(
    request: Request, cookie_token: str = Depends(token_utils.check_access_token)
):
    """Страница с пользовательскими аффирмациями"""
    data_return = {
        "request": request,
        "content_template": None,
        "user": True,
    }
    if not cookie_token:
        # Определяем контент в зависимости от авторизации
        data_return = {
            "request": request,
            "content_template": "auth_widget.html",
            "user": None,
        }

    return templates.TemplateResponse(
        "base.html",
        data_return,
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
                                "affirm": response.get("tasks", []),
                                "settings": response.get("settings", []),
                            }
                            return data_dict

        finally:
            await connection.close()
            logger.info("Соединение с RabbitMQ закрыто")
        # Проверка ответа и возврат шаблона
        if not response:
            raise HTTPException(500, "No response from /tasks")

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content", include_in_schema=settings.run.dev_mode)
async def get_content(
    request: Request, user: str | bool = Depends(token_utils.check_access_token)
):
    # Проверка авторизации (должен быть access_token)
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

    payload = await token_utils.decode_jwt(user)
    user_id: int = int(payload.get("user_id"))
    user: User = await crud_manager.user.get_one(field="id", value=user_id)

    user_data = {
        "id": user.tg_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    }

    if page in ("/affirmations", "affirmations"):
        data_dict = await get_affirmations_data(user_data)
        data_dict["request"] = request
        html_content = templates.TemplateResponse(content_template, data_dict)
        logger.info(f"Возвращен шаблон {content_template}")
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


@router.get("/content/{page_name}", include_in_schema=settings.run.dev_mode)
async def get_content(
    request: Request,
    user: str | bool = Depends(token_utils.check_access_token),
    page_name: str = "user",
) -> JSONResponse:
    # Проверка авторизации (должен быть access_token)
    if not user:
        return JSONResponse(
            content={"status": "Unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED
        )
