from typing import Annotated

from fastapi import Depends
from faststream.rabbit import RabbitBroker, fastapi

from config import settings

rabbitmq_broker = fastapi.RabbitRouter(
    settings.rabbit.url,
)


def get_broker() -> RabbitBroker:
    return rabbitmq_broker.broker


GetRabbitBroker = Annotated[
    RabbitBroker,
    Depends(get_broker),
]
