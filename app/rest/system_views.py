from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.config import settings
from paths_constants import FRONTEND_DIR_PATH

router = APIRouter()


@router.get(
    "/favicon.ico",
    include_in_schema=settings.run.dev_mode,
)
async def favicon() -> FileResponse:
    """
    Returns the website's favicon file.
    """
    return FileResponse(
        FRONTEND_DIR_PATH / "static" / "favicon.ico",
        media_type="image/vnd.microsoft.icon",
    )


@router.get(
    "/robots.txt",
    include_in_schema=settings.run.dev_mode,
)
async def robots() -> FileResponse:
    """
    Returns the `robots.txt` file for search engine indexing rules.
    """
    return FileResponse(
        FRONTEND_DIR_PATH / "static" / "robots.txt",
        media_type="text/plain",
    )
