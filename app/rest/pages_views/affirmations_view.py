import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import jwt_helper
from core.config import settings
from misc.flash_messages import flash
from misc.rabbitmq_broker import rabbitmq_broker
from paths_constants import templates
from rest.pages_views.dependencies.affirmations import (
    delete_user_affirmation,
    get_dict_with_user_affirmations,
    get_user_settings,
)
from rest.pages_views.dependencies.user_data import (
    get_user_data_by_access_token,
    return_data_for_user_profile_template,
)

from .redirect import redirect_to_login_page
from .schemas.user_data import UserDataReadSchema

router = APIRouter(
    tags=["Page views"],
)
log = logging.getLogger(__name__)


@router.get(
    "/affirmations",
    name="affirmations:list-page",
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
    user_settings: Annotated[
        dict[str, Any],
        Depends(get_user_settings),
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
    context.update(settings=user_settings)
    return templates.TemplateResponse(
        "pages/affirmations.html",
        context=context,
    )


@router.delete(
    "/affirmations/{affirmation_id}",
    name="affirmations:delete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(jwt_helper.strict_validate_access_token),
        Depends(delete_user_affirmation),
    ],
)
def delete_affirmation(
    request: Request,
    affirmation_id: int,
) -> JSONResponse:
    flash(
        request,
        message="Affirmation deleted",
        category="success",
    )
    log.info("Deleting affirmation id=%s", affirmation_id)
    return JSONResponse(
        {"redirect": str(request.url_for("affirmations:list-page"))},
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
