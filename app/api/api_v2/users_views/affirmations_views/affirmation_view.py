from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends

from api.api_v2.auth import token_utils
from api.api_v2.pages_views.dependencies import get_dict_with_user_affirmations

router = APIRouter()


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
    list_of_affirmations = cast(
        list[dict[str, Any]],
        affirmations.get("affirm", []),
    )
    return list_of_affirmations
