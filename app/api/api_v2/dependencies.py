from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from starlette import status


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
