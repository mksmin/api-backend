from typing import Annotated, Any

from fastapi import Depends
from starlette.requests import Request

from api.api_v2.auth import access_token_helper
from core.crud import GetCRUDService
from rest.pages_views.schemas.user_data import UserDataReadSchema


async def get_user_data_by_access_token(
    crud_service: GetCRUDService,
    user_id: str = Depends(
        access_token_helper.strict_validate_access_token,
    ),
) -> UserDataReadSchema | None:
    user = await crud_service.user.get_by_id_or_uuid(user_id)
    return UserDataReadSchema(
        id=user_id,
        tg_id=user.tg_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        photo_url="https://t.me/i/userpic/320/KAW0oZ7WjH_Mp1p43zuUi2lzp_IW2rxF954-zq5f3us.jpg",
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
