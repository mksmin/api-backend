import aio_pika

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.core import settings


router = APIRouter()


class TaskRequest(BaseModel):
    request: str
    endpoint: str
    data: dict


async def send_to_rabbit(message: str):
    connection = await aio_pika.connect_robust(f"{settings.rabbit.url}")
    channel = await connection.channel()
    await channel.declare_queue("tasks")
    await channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()), routing_key="tasks"
    )
    await connection.close()


@router.post("/create_task")
async def create_task(task: TaskRequest):
    await send_to_rabbit(task.json())
    return {"status": "Task queued"}


@router.post("/tasks", response_model=None)
async def tmp_create_tasks(data=Body()):
    pass
