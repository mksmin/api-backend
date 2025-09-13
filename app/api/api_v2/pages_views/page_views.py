from typing import Any
from urllib.request import Request

from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from core import settings

from .dependencies import (
    TEMPLATES,
    get_dict_with_user_affirmations,
    return_data_for_user_profile_template,
    rmq_router,
)

router = APIRouter(
    tags=["Page views"],
)


@router.get(
    "/affirmations",
    include_in_schema=settings.run.dev_mode,
)
async def page_user_affirmations(
    affirmations: dict[str, Any] = Depends(get_dict_with_user_affirmations),
) -> HTMLResponse:
    """Страница с пользовательскими аффирмациями"""

    return TEMPLATES.TemplateResponse(
        "pages/affirmations.html",
        affirmations,
    )


@router.get(
    "/profile",
    include_in_schema=settings.run.dev_mode,
)
async def page_profile(
    template_data: dict[str, Any] = Depends(return_data_for_user_profile_template),
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    return TEMPLATES.TemplateResponse(
        "profiles/profile.html",
        template_data,
    )


router.include_router(rmq_router)
