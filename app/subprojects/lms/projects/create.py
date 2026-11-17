from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Form
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from config import settings
from core.crud import GetCRUDService
from schemas import ProjectCreateSchema

router = APIRouter()


@router.get(
    "/new",
    name="lms-project:create",
    include_in_schema=settings.run.dev_mode,
)
async def get_page_project_create(
    request: Request,
    project_in: Annotated[
        ProjectCreateSchema,
        Form(),
    ],
    crud_service: GetCRUDService,
) -> HTMLResponse:
    pass
