"""
# TODO: Видимо это временный модуль, который когда то был костылем
# TODO: Удалить со временем
"""

from fastapi import APIRouter, status
from fastapi.params import Depends

from .dependencies import send_to_rabbit

router = APIRouter()


@router.post(
    "/create_task",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(send_to_rabbit),
    ],
)
async def create_task() -> str:
    return "Task queued"
