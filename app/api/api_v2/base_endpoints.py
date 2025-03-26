# import lib
import hashlib
import hmac
import json
import pprint
from urllib.parse import parse_qsl, unquote

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
    """
    Returns the index HTML file.

    Returns:
        FileResponse: The index HTML file.
    """
    index_html = cwd_project_path.parent / "html/index.html"
    return FileResponse(index_html)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Returns the favicon ICO file.

    Returns:
        FileResponse: The favicon ICO file.
    """
    favicon_path = cwd_project_path.parent / "html/favicon.ico"
    return FileResponse(favicon_path)


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    """
    Returns the robots TXT file.

    Returns:
        FileResponse: The robots TXT file.
    """
    robots_path = cwd_project_path.parent / "robots.txt"
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
    media_path = cwd_project_path.parent / "html" / name_html
    result, status = await check_path(media_path)
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
    media_path = cwd_project_path.parent / "html/media" / name_media
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
    media_path = cwd_project_path.parent / "html/style" / name_style
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
    script_path = cwd_project_path.parent / "html/scripts" / name_script
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
    profile_html = cwd_project_path.parent / "html/profile.html"
    return FileResponse(profile_html)


def verify_telegram_data(init_data: str) -> bool:
    """
    Проверяет валидность данных от Telegram Web Apps
    """
    try:
        vals = {
            k: unquote(v) for k, v in [s.split("=", 1) for s in init_data.split("&")]
        }
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(vals.items()) if k != "hash"
        )

        secret_key = hmac.new(
            "WebAppData".encode(), settings.api.bot_token.encode(), hashlib.sha256
        ).digest()
        h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
        return h.hexdigest() == vals["hash"]
    except Exception as e:
        print(f"Verification error: {e}")
        return False


@router.post("/verify")
async def verify_telegram(request: Request):
    try:
        data = await request.json()
        # print(f"data: {data}")

        init_data = data.get("initData")
        # print(f"init_data: {init_data}")

        if not init_data:
            raise HTTPException(status_code=400, detail="Missing initData")

        if verify_telegram_data(init_data):
            return {"status": "success", "message": "Data verified"}
        else:
            raise HTTPException(status_code=401, detail="Invalid data")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
