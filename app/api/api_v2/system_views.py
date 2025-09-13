from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from api.api_v2.dependencies import PUBLIC_DIR
from core import settings

router = APIRouter()


@router.get(
    "/favicon.ico",
    include_in_schema=settings.run.dev_mode,
)
async def favicon() -> FileResponse:
    """
    Returns the website's favicon file.

    Returns:
        FileResponse: Response object containing the `favicon.ico` file
                      located in the `STATIC_DIR` directory.
    """
    return FileResponse(PUBLIC_DIR / "favicon.ico")


@router.get(
    "/robots.txt",
    include_in_schema=settings.run.dev_mode,
)
async def robots() -> FileResponse:
    """
    Returns the `robots.txt` file for search engine indexing rules.

    Returns:
        FileResponse: The contents of the `robots.txt` file located in the
                      `STATIC_DIR` directory with HTTP 200 OK status.
    """
    return FileResponse(PUBLIC_DIR / "robots.txt")
