from typing import Annotated
from typing import Any

from fastapi import Depends
from fastapi.requests import Request

from auth import jwt_helper
from core.crud import GetCRUDService
from rest.pages_views.schemas.user_data import UserDataReadSchema


async def get_user_data_by_access_token(
    crud_service: GetCRUDService,
    user_id: str = Depends(
        jwt_helper.strict_validate_access_token,
    ),
) -> UserDataReadSchema | None:
    user = await crud_service.user.get_by_id_or_uuid(user_id)
    return UserDataReadSchema(
        id=user_id,
        tg_id=user.tg_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        photo_url="/static/media/nonePhoto.png",
    )


async def return_data_for_user_profile_template(
    request: Request,
    user_data: Annotated[
        UserDataReadSchema | None,
        Depends(get_user_data_by_access_token),
    ],
) -> dict[str, Any]:
    return {
        "request": request,
        "auth_widget": None if user_data else "auth_widget.html",
        "user": user_data.model_dump() if user_data else None,
    }
