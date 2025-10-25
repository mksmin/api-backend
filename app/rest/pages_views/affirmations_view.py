from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from core.config import settings
from misc.rabbitmq_broker import rabbitmq_broker
from paths_constants import templates

from .dependencies.affirmations import get_dict_with_user_affirmations
from .dependencies.user_data import (
    get_user_data_by_access_token,
    return_data_for_user_profile_template,
)
from .redirect import redirect_to_login_page
from .schemas.user_data import UserDataReadSchema

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
    request: Request,
    user_data: Annotated[
        UserDataReadSchema,
        Depends(get_user_data_by_access_token),
    ],
    affirmations: Annotated[
        dict[str, Any],
        Depends(get_dict_with_user_affirmations),
    ],
) -> HTMLResponse:
    """Страница с пользовательскими аффирмациями"""
    context = {}
    context_data = {
        "request": request,
        "user": user_data.model_dump(),
        **affirmations,
    }
    context.update(context_data)
    context.update(
        settings={
            "count_tasks": "--",
            "time_send": "--",
        },
    )
    return templates.TemplateResponse(
        "pages/affirmations.html",
        context=context,
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


router.include_router(rabbitmq_broker)
