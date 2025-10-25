from typing import Any

from pydantic import BaseModel


class GetListAffirmationsResponse(BaseModel):
    affirmations: list[dict[str, Any] | None] = []
