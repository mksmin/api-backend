import asyncio
import json
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, HTTPException, status

if TYPE_CHECKING:
    from faststream.rabbit import RabbitMessage

from api.api_v2.auth import token_utils
from core.crud import crud_manager
from rest.pages_views.dependencies import get_broker


async def delete_user_affirmation(
    affirmation_id: int,
    user_id: Annotated[str, Depends(token_utils.strict_validate_access_token)],
) -> bool:
    broker = get_broker()
    try:
        user = await crud_manager.user.get_one(
            field="id",
            value=user_id,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

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

    except asyncio.TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from e

    else:
        return True
