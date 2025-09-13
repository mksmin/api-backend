from pathlib import Path
from typing import Any, Callable, Coroutine

from fastapi import HTTPException
from starlette import status

from core import settings

BASE_DIR = Path.cwd().resolve().parent  # project working directory ../app
FRONTEND_DIR = (
    (BASE_DIR / "api-frontend") if settings.run.dev_mode else (BASE_DIR.parent / "frontend")
)
SRC_DIR = FRONTEND_DIR / "src"
PUBLIC_DIR = FRONTEND_DIR / "public"
NOT_FOUND_PAGE_404 = FRONTEND_DIR / "src/404.html"


def file_dependency(
    base_dir: Path,
    sub_dir: str | None = None,
) -> Callable[[str], Coroutine[Any, Any, Path]]:
    async def _get_file(
        name_file: str,
    ) -> Path:
        file_path = base_dir / sub_dir / name_file if sub_dir else base_dir / name_file
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {name_file} not found",
            )
        return file_path

    return _get_file
