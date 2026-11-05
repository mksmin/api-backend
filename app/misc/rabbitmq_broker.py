from typing import Annotated

from fastapi import Depends
from faststream.rabbit import RabbitBroker
from faststream.rabbit import fastapi

from app_exceptions import RabbitMQServiceUnavailableError
from config import settings

broker = RabbitBroker(
    settings.rabbit.url,
    fail_fast=False,
    reconnect_interval=60.0,
    timeout=8.0,
)


async def get_broker() -> RabbitBroker:
    if not await broker.ping(
        timeout=0.2,
    ):
        raise RabbitMQServiceUnavailableError
    return broker


GetRabbitBroker = Annotated[
    RabbitBroker,
    Depends(get_broker),
]
