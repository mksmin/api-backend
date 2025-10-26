import asyncio
import json
from typing import (
    Annotated,
    Any,
)

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.params import Query

from api.api_v2.auth import access_token_helper
from app_exceptions import UserNotFoundError
from app_exceptions.exceptions import RabbitMQServiceUnavailableError
from core.crud import GetCRUDService
from misc.rabbitmq_broker import GetRabbitBroker
from rest.pages_views.dependencies.user_data import get_user_data_by_access_token
from rest.pages_views.schemas import (
    GetListAffirmationsResponse,
    UserDataReadSchema,
)
from rest.pages_views.schemas.affirmations_data import GetUserSettingsResponse


async def get_dict_with_user_affirmations(
    user_data: Annotated[
        UserDataReadSchema,
        Depends(get_user_data_by_access_token),
    ],
    broker: GetRabbitBroker,
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
    try:
        message = {
            "type": "GetPaginatedAffirmations",
            "payload": {
                "user_tg": user_data.tg_id,
                "limit": limit,
                "offset": offset,
            },
        }
        result = await broker.request(
            message,
            queue="qry.affirmations",
            timeout=3,
        )
        decoded_broker_response = json.loads(
            result.body.decode("utf-8"),
        )
        return GetListAffirmationsResponse.model_validate(
            decoded_broker_response,
        ).model_dump()
    except asyncio.TimeoutError as e:
        raise RabbitMQServiceUnavailableError from e


async def get_user_settings(
    user_data: Annotated[
        UserDataReadSchema,
        Depends(get_user_data_by_access_token),
    ],
    broker: GetRabbitBroker,
) -> dict[str, Any]:
    try:
        message = {
            "type": "GetUserSettings",
            "payload": {
                "user_tg": user_data.tg_id,
            },
        }

        result = await broker.request(
            message,
            queue="qry.affirmations",
            timeout=3,
        )
        decoded_broker_response = json.loads(
            result.body.decode("utf-8"),
        )
        return GetUserSettingsResponse.model_validate(
            decoded_broker_response,
        ).model_dump()
    except asyncio.TimeoutError as e:
        raise RabbitMQServiceUnavailableError from e


async def delete_user_affirmation(
    affirmation_id: int,
    user_id: Annotated[str, Depends(access_token_helper.strict_validate_access_token)],
    crud_service: GetCRUDService,
    broker: GetRabbitBroker,
) -> bool:
    try:
        user = await crud_service.user.get_by_id_or_uuid(user_id)
        message = {
            "type": "RemoveAffirmation",
            "payload": {
                "user_tg": user.tg_id,
                "affirmation_id": affirmation_id,
            },
        }

        await broker.publish(
            message,
            queue="cmd.affirmations",
            timeout=3,
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    except asyncio.TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from e
    else:
        return True
