import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import Depends
from fastapi.params import Query
from fastapi.requests import Request
from faststream.rabbit import RabbitBroker, RabbitMessage, fastapi
from pydantic import BaseModel

from api.api_v2.auth import token_utils
from core.config import settings
from core.crud import GetCRUDService

rmq_router = fastapi.RabbitRouter(
    settings.rabbit.url,
)
log = logging.getLogger(__name__)


def get_broker() -> RabbitBroker:
    return rmq_router.broker


class UserDataReadSchema(BaseModel):
    id: int
    tg_id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    is_premium: bool
    photo_url: str | None
    language_code: str | None
    allows_write_to_pm: bool


async def return_user_data(
    crud_service: GetCRUDService,
    user_id: str = Depends(
        token_utils.soft_validate_access_token,
    ),
) -> UserDataReadSchema | None:
    if not user_id:
        return None

    user = await crud_service.user.get_by_id_or_uuid(user_id)

    return UserDataReadSchema(
        id=user_id,
        tg_id=user.tg_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        is_premium=True,
        photo_url="https://t.me/i/userpic/320/KAW0oZ7WjH_Mp1p43zuUi2lzp_IW2rxF954-zq5f3us.jpg",
        language_code="ru",
        allows_write_to_pm=True,
    )


async def return_data_for_user_profile_template(
    request: Request,
    user_data: Annotated[
        UserDataReadSchema | None,
        Depends(return_user_data),
    ],
) -> dict[str, Any]:
    return {
        "request": request,
        "auth_widget": None if user_data else "auth_widget.html",
        "user": user_data.model_dump() if user_data else None,
    }


async def get_dict_with_user_affirmations(
    request: Request,
    user_data: Annotated[
        UserDataReadSchema | None,
        Depends(return_user_data),
    ],
    limit: Annotated[
        int,
        Query(
            title="Limit",
            description="Количество аффирмаций",
        ),
    ] = 15,
    offset: Annotated[
        int,
        Query(
            title="Offset",
            description="Смещение",
        ),
    ] = 0,
) -> dict[str, Any]:
    if not user_data:
        return {
            "request": request,
            "auth_widget": "auth_widget.html",
        }
    broker = get_broker()
    try:
        rabbit_request: dict[str, Any] = {
            "command": "get_paginated_tasks",
            "payload": {
                "user_tg": user_data.tg_id,
                "limit": limit,
                "offset": offset,
            },
        }
        result: RabbitMessage = await broker.request(
            rabbit_request,
            queue="affirmations",
            timeout=3,
        )
        decoded_result = result.body.decode("utf-8")
        affirmations_list: list[dict[str, Any]] = json.loads(decoded_result)
        return {
            "request": request,
            "user": user_data.model_dump(),
            "affirm": affirmations_list,
            "settings": {
                "count_tasks": "--",
                "time_send": "--",
            },
        }
    except asyncio.TimeoutError:
        log.exception(
            "Timeout error while getting paginated tasks",
        )
        return {
            "request": request,
            "user": user_data.model_dump(),
            "error": "Сервис временно недоступен",
        }
