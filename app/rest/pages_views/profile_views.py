from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_csrf_protect import CsrfProtect

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
    request: Request,
    template_data: Annotated[
        dict[str, Any],
        Depends(return_data_for_user_profile_template),
    ],
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
) -> HTMLResponse:
    """Страница с профилем пользователя"""
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()

    response = templates.TemplateResponse(
        request=request,
        name="profiles/profile.html",
        context={
            **template_data,
            "csrf_token": csrf_token,
        },
    )
    csrf_protect.set_csrf_cookie(
        signed_token,
        response,
    )
    return response
