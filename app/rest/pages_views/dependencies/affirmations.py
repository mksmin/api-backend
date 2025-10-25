import asyncio
import json
from typing import (
    TYPE_CHECKING,
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
from misc.rabbitmq_broker import get_broker
from rest.pages_views.dependencies.user_data import get_user_data_by_access_token
from rest.pages_views.schemas import (
    GetListAffirmationsResponse,
    UserDataReadSchema,
)

if TYPE_CHECKING:
    from faststream.rabbit import RabbitMessage


async def get_dict_with_user_affirmations(
    user_data: Annotated[
        UserDataReadSchema,
        Depends(get_user_data_by_access_token),
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
    try:
        broker = get_broker()
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


async def delete_user_affirmation(
    affirmation_id: int,
    user_id: Annotated[str, Depends(access_token_helper.strict_validate_access_token)],
    crud_service: GetCRUDService,
) -> bool:
    broker = get_broker()
    try:
        user = await crud_service.user.get_by_id_or_uuid(user_id)
        rabbit_request: dict[str, Any] = {
            "command": "mark_as_done",
            "payload": {
                "task_id": affirmation_id,
                "user_tg": user.tg_id,
            },
        }
        result: RabbitMessage = await broker.request(
            rabbit_request,
            queue="affirmations",
            timeout=3,
        )
        decoded_result = result.body.decode("utf-8")
        result_of_removing: dict[str, Any] = json.loads(decoded_result)

        if result_of_removing["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result_of_removing["message"],
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
