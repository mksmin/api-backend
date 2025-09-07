# import lib
import asyncio
import json

# import from lib
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from faststream.rabbit import fastapi, RabbitBroker, RabbitMessage
from pathlib import Path


# import from modules
from app.core import settings, logger, crud_manager
from app.core.database import User
from .auth import auth_utils, token_utils, auth_router, api_key_endpoints

router = APIRouter()
router.include_router(
    auth_router,
    tags=["Authentication"],
)
router.include_router(
    api_key_endpoints.router,
    tags=["Authentication"],
)

rmq_router = fastapi.RabbitRouter(
    settings.rabbit.url,
)

BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-frontend") if settings.run.dev_mode else (BASE_DIR / "frontend")
)
HTML_DIR = FRONTEND_DIR / "src"
STATIC_DIR = FRONTEND_DIR / "public"
templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")
not_found_404 = FRONTEND_DIR / "src/404.html"


def get_broker() -> RabbitBroker:
    return rmq_router.broker


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
    logger.info(f"Get affirmations data for user {user_data.get('id')}")
    broker = get_broker()
    try:
        rabbit_request = {
            "command": "get_paginated_tasks",
            "payload": {
                "user_tg": int(user_data.get("id")),
                "offset": 0,
                "limit": 100,
            },
        }
        result: RabbitMessage = await broker.request(
            message=rabbit_request,
            queue="affirmations",
            timeout=3,
        )
        decoded = result.body.decode("utf-8")
        dict_data: list[dict] = json.loads(decoded)
        return_data = {
            "user": user_data,
            "affirm": dict_data,
            "settings": None,
        }
        return return_data

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )


router.include_router(rmq_router)


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
