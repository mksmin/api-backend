# import lib
import hashlib
import hmac
import json
import pprint
from urllib.parse import parse_qsl

# import from lib
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

# import from modules
from app.core import settings, logger

router = APIRouter()
cwd_project_path = (
    Path(__file__).absolute().parent.parent.parent
)  # project working directory api_atomlab/app
not_found_404 = cwd_project_path.parent / "html/404.html"


async def check_path(path_file: Path):
    file_exists = Path(path_file).exists()

    if file_exists:
        return path_file, 200
    else:
        return not_found_404, 404


@router.get("/")
async def index_page():
    index_html = cwd_project_path.parent / "html/index.html"
    return FileResponse(index_html)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = cwd_project_path.parent / "html/favicon.ico"
    return FileResponse(favicon_path)


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    robots_path = cwd_project_path.parent / "robots.txt"
    return FileResponse(robots_path)


@router.get("/html/{name_html}", include_in_schema=False)
async def html_path(name_html: str):
    media_path = cwd_project_path.parent / "html" / name_html
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


#
@router.get("/media/{name_media}", include_in_schema=False)
async def html_path(name_media: str):
    media_path = cwd_project_path.parent / "html/media" / name_media
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@router.get("/style/{name_style}", include_in_schema=False)
async def html_path(name_style: str):
    media_path = cwd_project_path.parent / "html/style" / name_style
    result, status = await check_path(media_path)
    return FileResponse(result, status_code=status)


@router.get("/profile", include_in_schema=False)
async def user_profile_tg(request: Request):
    params = {
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
    }
    pprint.pprint(f"params: {params}")
    profile_html = cwd_project_path.parent / "html/profile.html"
    return FileResponse(profile_html)


def verify_telegram_data(init_data: str) -> bool:
    """
    Проверяет валидность данных от Telegram Web Apps
    """
    try:
        # Парсим данные
        parsed_data = dict(parse_qsl(init_data))

        # Извлекаем hash и сортируем параметры
        received_hash = parsed_data.pop("hash")
        data_check = []

        # Сортируем ключи в алфавитном порядке
        for key in sorted(parsed_data.keys()):
            data_check.append(f"{key}={parsed_data[key]}")

        data_check_string = "\n".join(data_check)

        # Создаем секретный ключ
        secret_key = hashlib.sha256(settings.api.bot_token.encode()).digest()

        # Вычисляем HMAC
        computed_hash = hmac.new(
            secret_key, data_check_string.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        return computed_hash == received_hash
    except Exception as e:
        print(f"Verification error: {e}")
        return False


@router.post("/verify")
async def verify_telegram(request: Request):
    try:
        data = await request.json()
        print(f"data: {data}")

        init_data = data.get("initData")
        print(f"init_data: {init_data}")

        if not init_data:
            raise HTTPException(status_code=400, detail="Missing initData")

        if verify_telegram_data(init_data):
            return {"status": "success", "message": "Data verified"}
        else:
            raise HTTPException(status_code=401, detail="Invalid data")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
