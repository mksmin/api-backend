from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from app_exceptions import InvalidUUIDError


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


def validate_uuid_str(
    project_uuid: str,
) -> UUID:
    try:
        return UUID(project_uuid)
    except ValueError as e:
        raise InvalidUUIDError from e
