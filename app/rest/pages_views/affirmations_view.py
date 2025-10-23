from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from core.config import settings
from paths_constants import templates

from .dependencies import (
    get_dict_with_user_affirmations,
    redirect_to_login_page,
    return_data_for_user_profile_template,
    rmq_router,
)

router = APIRouter(
    tags=["Page views"],
)


@router.get(
    "/affirmations",
    include_in_schema=settings.run.dev_mode,
    dependencies=[
        Depends(redirect_to_login_page),
    ],
)
async def page_user_affirmations(
    affirmations: Annotated[
        dict[str, Any],
        Depends(get_dict_with_user_affirmations),
    ],
) -> HTMLResponse:
    """Страница с пользовательскими аффирмациями"""

    return templates.TemplateResponse(
        "pages/affirmations.html",
        affirmations,
    )


@router.get(
    "/profile",
    include_in_schema=settings.run.dev_mode,
)
async def page_profile(
    template_data: Annotated[
        dict[str, Any],
        Depends(return_data_for_user_profile_template),
    ],
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    return templates.TemplateResponse(
        "profiles/profile.html",
        template_data,
    )


router.include_router(rmq_router)
