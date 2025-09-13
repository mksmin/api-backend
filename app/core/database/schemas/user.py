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

    external_id_bid: Optional[int] = None
    external_date_bid: Optional[datetime] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None

    email: Optional[str] = None
    mobile: Optional[str] = None
    tg_id: Optional[int] = None
    username: Optional[str] = None

    citizenship: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    study_place: Optional[str] = None
    grade_level: Optional[str] = None

    birth_date: Optional[datetime] = None
    sex: Optional[str] = None

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
                logger.error(f"Error processing key: {key}, value: {value}: {str(e)}")
                raise

        return process_result

    @classmethod
    def parse_datetime(cls, value: Any) -> datetime:
        try:
            return parser.parse(value) if isinstance(value, str) else value
        except Exception as e:
            raise ValueError(f"Invalid datetime format for value: {value}: {str(e)}")

    model_config = ConfigDict(from_attributes=True, extra="ignore")
