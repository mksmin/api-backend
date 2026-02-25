from pathlib import Path
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.responses import FileResponse

from api.api_v2.dependencies import file_dependency
from config import settings
from paths_constants import HTML_DIR

router = APIRouter()


@router.get(
    "/html/{name_file}",
    include_in_schema=settings.run.dev_mode,
)
async def get_static_html(
    name_file: str,  # noqa: ARG001
    file_path: Annotated[
        Path,
        Depends(
            file_dependency(base_dir=HTML_DIR),
        ),
    ],
) -> FileResponse:
    """
    Returns a requested HTML file from the frontend source directory.
    """
    return FileResponse(
        file_path,
        status_code=status.HTTP_200_OK,
    )
