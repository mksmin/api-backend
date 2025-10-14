from fastapi import APIRouter
from fastapi.responses import FileResponse

from paths_constants import HTML_DIR
from rest.static_views import router as static_router
from rest.system_views import router as system_router

router = APIRouter(
    tags=["Main Views"],
)


@router.get("/")
async def index_page() -> FileResponse:
    """
    Returns the main application HTML file.

    Returns:
        FileResponse: Response object containing the `index.html` file
                      located in the `HTML_DIR` directory.

    Description:
        This endpoint serves as the entry point for the frontend application.
        It constructs the file path as `HTML_DIR / "index.html"`.
    """
    index_html = HTML_DIR / "index.html"
    return FileResponse(index_html)


router.include_router(system_router)
router.include_router(static_router)
