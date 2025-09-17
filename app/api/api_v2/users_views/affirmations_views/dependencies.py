import asyncio
import json
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException, status

if TYPE_CHECKING:
    from faststream.rabbit import RabbitMessage

from api.api_v2.pages_views.dependencies import get_broker


async def delete_user_affirmation(
    affirmation_id: int,
) -> bool:
    broker = get_broker()
    try:
        rabbit_request: dict[str, Any] = {
            "command": "mark_as_done",
            "payload": {
                "task_id": affirmation_id,
            },
        }
        result: RabbitMessage = await broker.request(
            rabbit_request,
            queue="affirmations",
            timeout=3,
        )
        decoded_result = result.body.decode("utf-8")
        result_of_removing: bool = json.loads(decoded_result)
        if not result_of_removing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Something went wrong",
            )

    except asyncio.TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from e

    else:
        return result_of_removing
