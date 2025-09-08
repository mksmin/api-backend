from typing import Any

from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from core import settings

from .dependencies import TEMPLATES, return_template_for_affirmations

router = APIRouter(
    tags=["Affirmations"],
)


@router.get(
    "/affirmations",
    include_in_schema=settings.run.dev_mode,
)
async def page_user_affirmations(
    template_data: dict[str, Any] = Depends(return_template_for_affirmations),
) -> HTMLResponse:
    """Страница с пользовательскими аффирмациями"""
    return TEMPLATES.TemplateResponse(
        "base.html",
        template_data,
    )
