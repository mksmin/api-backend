from datetime import datetime
from typing import Any, Optional

from dateutil import parser
from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    root_validator,
)

from core import logger


class UserSchema(BaseModel):
    uuid: str

    external_id_bid: int | None = None
    external_date_bid: datetime | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None

    email: str | None = None
    mobile: str | None = None
    tg_id: int | None = None
    username: str | None = None

    citizenship: str | None = None
    country: str | None = None
    city: str | None = None
    timezone: str | None = None
    study_place: str | None = None
    grade_level: str | None = None

    birth_date: datetime | None = None
    sex: str | None = None

    @model_validator(mode="before")
    @classmethod
    def prevalidate(
        cls,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        process_result: dict[str, Any] = {}

        for key, value in values.items():

            if key not in cls.model_fields:
                logger.warning(f"Skipping key: {key}")
                continue
            try:
                if key in ("external_date_bid", "birth_date"):
                    process_result[key] = cls.parse_datetime(value)
                elif key == "timezone":
                    process_result[key] = str(value)
                elif key in ("tg_id", "external_id_bid"):
                    process_result[key] = int(value)
                else:
                    process_result[key] = str(value)
            except Exception as e:
                logger.error(f"Error processing key: {key}, value: {value}: {e!s}")
                raise

        return process_result

    @classmethod
    def parse_datetime(
        cls,
        value: Any,  # noqa: ANN401
    ) -> datetime:
        try:
            return parser.parse(value) if isinstance(value, str) else value
        except Exception as e:
            msg_error = f"Invalid datetime format for value: {value}: {e!s}"
            raise ValueError(msg_error) from e

    model_config = ConfigDict(from_attributes=True, extra="ignore")
