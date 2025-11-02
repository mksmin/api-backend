import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from starlette.requests import Request

from api.api_v2.auth import access_token_helper
from misc.flash_messages import flash
from rest.pages_views.dependencies.affirmations import (
    delete_user_affirmation,
    get_dict_with_user_affirmations,
)

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    dependencies=[
        Depends(access_token_helper.strict_validate_access_token),
    ],
)
def get_user_affirmations(
    affirmations: Annotated[
        dict[str, Any],
        Depends(get_dict_with_user_affirmations),
    ],
) -> dict[str, Any]:
    return affirmations


@router.delete(
    "/{affirmation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(access_token_helper.strict_validate_access_token),
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
