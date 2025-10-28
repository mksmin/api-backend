from datetime import time
from typing import Any

from pydantic import BaseModel


class GetListAffirmationsResponse(BaseModel):
    affirmations: list[dict[str, Any] | None] = []


class SettingsUserTGResponse(BaseModel):
    user_tg: int


class GetUserSettingsResponse(BaseModel):
    user: SettingsUserTGResponse
    count_tasks: int
    send_time: time
    send_enable: bool
