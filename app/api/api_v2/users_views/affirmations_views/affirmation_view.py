import logging
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, status

from api.api_v2.auth import token_utils
from rest.pages_views.dependencies import get_dict_with_user_affirmations

from .dependencies import delete_user_affirmation

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    dependencies=[
        Depends(token_utils.strict_validate_access_token),
    ],
)
def get_user_affirmations(
    affirmations: Annotated[
        dict[str, Any],
        Depends(get_dict_with_user_affirmations),
    ],
) -> list[dict[str, Any]]:
    return cast(
        "list[dict[str, Any]]",
        affirmations.get("affirm", []),
    )


@router.delete(
    "/{affirmation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(token_utils.strict_validate_access_token),
        Depends(delete_user_affirmation),
    ],
)
def delete_affirmation(
    affirmation_id: int,
) -> None:
    log.info("Deleting affirmation id=%s", affirmation_id)
