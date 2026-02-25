import logging
from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from auth import jwt_helper
from misc.flash_messages import flash
from rest.pages_views.dependencies.affirmations import delete_user_affirmation
from rest.pages_views.dependencies.affirmations import get_dict_with_user_affirmations
from rest.pages_views.dependencies.affirmations import patch_user_affirmation_settings
from rest.pages_views.dependencies.affirmations import update_user_affirmation

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    dependencies=[
        Depends(jwt_helper.strict_validate_access_token),
    ],
)
def get_user_affirmations(
    affirmations: Annotated[
        dict[str, Any],
        Depends(get_dict_with_user_affirmations),
    ],
) -> dict[str, Any]:
    return affirmations


@router.put(
    "/{affirmation_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(jwt_helper.strict_validate_access_token),
        Depends(update_user_affirmation),
    ],
)
def update_affirmation(
    request: Request,
    affirmation_id: int,
) -> JSONResponse:
    log.info("Updating affirmation id=%s", affirmation_id)
    return JSONResponse(
        {
            "redirect": str(
                request.url_for("affirmations:list-page"),
            ),
        },
    )


@router.delete(
    "/{affirmation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(jwt_helper.strict_validate_access_token),
        Depends(delete_user_affirmation),
    ],
)
def delete_affirmation(
    request: Request,
    affirmation_id: int,
) -> None:
    flash(
        request,
        message="Аффирмация удалена",
        category="success",
    )
    log.info("Deleting affirmation id=%s", affirmation_id)


@router.patch(
    "/settings",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(jwt_helper.strict_validate_access_token),
        Depends(patch_user_affirmation_settings),
    ],
)
async def patch_user_settings() -> None:
    """Обновление настроек аффирмаций"""
