from typing import Any

import aio_pika
from pydantic import BaseModel

from core import settings


class TaskRequest(BaseModel):
    request: str
    endpoint: str
    data: dict[str, Any]


async def send_to_rabbit(
    task: TaskRequest,
) -> None:
    message = task.model_dump_json()
    connection = await aio_pika.connect_robust(settings.rabbit.url)
    channel = await connection.channel()
    await channel.declare_queue("tasks")
    await channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()), routing_key="tasks"
    )
    await connection.close()
