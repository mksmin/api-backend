# import lib
import hashlib
import hmac
import json
import pprint
from urllib.parse import parse_qsl, unquote

# import from lib
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# import from modules
from app.core import settings, logger

router = APIRouter()
BASE_DIR = Path.cwd().parent  # project working directory api_atomlab/app
FRONTEND_DIR = (
    (BASE_DIR / "api-atom-front") if settings.run.dev_mode else (BASE_DIR / "frontend")
)
HTML_DIR = FRONTEND_DIR / "src"
STATIC_DIR = FRONTEND_DIR / "public"

templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")

# print(f"BASE_DIR: {BASE_DIR}")
# print(f"FRONTEND_DIR: {FRONTEND_DIR}")
# print(f"HTML_DIR: {HTML_DIR}")
not_found_404 = FRONTEND_DIR / "src/404.html"
# print(f"not_found_404: {not_found_404}")


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


@router.get("/profile", include_in_schema=False)
async def user_profile_tg(request: Request):
    """
    Returns the user profile HTML file.

    Args:
        request (Request): The incoming request object.

    Returns:
        FileResponse: The user profile HTML file.
    """
    params = {
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
    }
    # pprint.pprint(f"params: {params}")
    profile_html = HTML_DIR / "profile.html"
    profile_html = FRONTEND_DIR / "templates/base.html"

    return FileResponse(profile_html)


def verify_telegram_data(init_data: str) -> dict | bool:
    """
    Проверяет валидность данных от Telegram Web Apps
    """
    try:
        # Парсинг данных из initData
        values = dict()
        for splitted in init_data.split("&"):
            key, value = splitted.split("=", 1)
            values[key] = unquote(value)

        # Проверка хэша
        # Преобразование данных в строку для хэширования
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(values.items()) if key != "hash"
        )
        # Генерация секретного ключа
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.api.bot_token.encode(),
            hashlib.sha256,
        ).digest()

        # Генерация хэша
        generated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Защита от атаки по времени
        if not hmac.compare_digest(generated_hash, values["hash"]):
            return False

        # Парсинг данных из initData
        user_data = json.loads(values.get("user", "{}"))
        required_fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "language_code",
            "photo_url",
        ]
        if not all(field in user_data for field in required_fields):
            print(
                f"Required fields missing: {[field for field in required_fields if field not in user_data]}"
            )
            return False
        return {
            "id": user_data["id"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "username": user_data["username"],
            "is_premium": user_data["is_premium"],
            "photo_url": user_data["photo_url"],
            "language_code": user_data["language_code"],
            "allows_write_to_pm": user_data["allows_write_to_pm"],
        }

        # vals = {
        #     k: unquote(v) for k, v in [s.split("=", 1) for s in init_data.split("&")]
        # }
        #
        # print(f"vals: {vals}")
        # print(f"values: {values}")
        # data_check_string2 = "\n".join(
        #     f"{k}={v}" for k, v in sorted(vals.items()) if k != "hash"
        # )
        # secret_key2 = hmac.new(
        #     "WebAppData".encode(), settings.api.bot_token.encode(), hashlib.sha256
        # ).digest()
        #
        # h = hmac.new(secret_key2, data_check_string2.encode(), hashlib.sha256)

        # print(f"h.hexdigest(): {h.hexdigest()}")
        # return h.hexdigest() == vals["hash"]

    except Exception as e:
        raise ValueError(f"Verification error: {e}")
        # return False


@router.post("/verify", response_class=HTMLResponse)
async def verify_telegram(request: Request):
    try:
        # Получение init данных из запроса
        data = await request.json()
        init_data = data.get("initData")

        if not init_data:
            return HTTPException(status_code=400, detail="Missing initData")

        user_data = verify_telegram_data(init_data)
        if not user_data:
            return HTTPException(status_code=401, detail="Invalid data")

        return templates.TemplateResponse(
            "profile.html", {"request": request, "user": user_data}
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
