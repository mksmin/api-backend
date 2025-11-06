from datetime import time

from pydantic import BaseModel, Field


class ChangeAffirmationsSettings(BaseModel):
    count_tasks: int | None = Field(
        None,
        ge=1,
        le=5,
    )
    send_time: time | None = None
    send_enable: bool | None = None
