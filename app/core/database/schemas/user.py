import logging
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

logger = logging.getLogger(__name__)


class UserSchema(BaseModel):
    uuid: str

    first_name: str | None = None
    last_name: str | None = None
    tg_id: int | None = None
    username: str | None = None

    @model_validator(mode="before")
    @classmethod
    def prevalidate(
        cls,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        process_result: dict[str, Any] = {}

        for key, value in values.items():
            if key not in cls.model_fields:
                logger.warning("Skipping key: %s", key)
                continue
            try:
                process_result[key] = (
                    int(value) if key in ("tg_id", "external_id_bid") else str(value)
                )
            except Exception:
                logger.exception("Error processing key: %s, value: %s", key, value)
                raise

        return process_result

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )
