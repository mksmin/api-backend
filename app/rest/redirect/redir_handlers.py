from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Body
from fastapi import status
from fastapi.responses import RedirectResponse

from config import settings

router = APIRouter(
    tags=["Redirects"],
)

actual_version = "/api/v2/"

path_mapping = {
    "users": actual_version + "users/",
}


@router.post(
    "/tasks",
    include_in_schema=settings.run.dev_mode,
)
async def rabbit_task_create(
    data: Annotated[dict[str, Any], Body()],  # noqa: ARG001
) -> RedirectResponse:
    return RedirectResponse(
        url=f"{path_mapping['users']}tasks",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )
