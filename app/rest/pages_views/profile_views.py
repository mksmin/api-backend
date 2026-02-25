from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import HTMLResponse

from config import settings
from paths_constants import templates
from rest.pages_views.dependencies.user_data import (
    return_data_for_user_profile_template,
)
from rest.pages_views.redirect import redirect_to_login_page

router = APIRouter()


@router.get(
    "/profile",
    name="profiles:user-profile",
    include_in_schema=settings.run.dev_mode,
    dependencies=[
        Depends(redirect_to_login_page),
    ],
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
