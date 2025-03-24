from datetime import datetime
from typing import Optional

from dateutil import parser

from pydantic import BaseModel, root_validator, ConfigDict, model_validator

from app.core import logger


class UserSchema(BaseModel):
    id_bid_ya: int
    date_bid_ya: datetime
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None

    email: Optional[str] = None
    mobile: Optional[str] = None
    tg_id: Optional[int] = None

    citizenship: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    study_place: Optional[str] = None
    grade_level: Optional[str] = None

    birth_date: Optional[datetime] = None
    sex: Optional[str] = None

    project_id: Optional[int] = None
    track: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def prevalidate(cls, values: dict[str, any]) -> dict[str, any]:
        process_result = {}

        for key, value in values.items():

            if key not in cls.model_fields:
                logger.warning(f"Skipping key: {key}")
                continue
            try:
                if key in ("date_bid_ya", "birth_date"):
                    process_result[key] = cls.parse_datetime(value)
                elif key == "timezone":
                    process_result[key] = str(value)
                elif key in ("tg_id", "id_bid_ya", "project_id"):
                    process_result[key] = int(value)
                else:
                    process_result[key] = str(value)
            except Exception as e:
                logger.error(f"Error processing key: {key}, value: {value}: {str(e)}")
                raise

        return process_result

    @classmethod
    def parse_datetime(cls, value: any) -> datetime:
        try:
            return parser.parse(value) if isinstance(value, str) else value
        except Exception as e:
            raise ValueError(f"Invalid datetime format for value: {value}: {str(e)}")

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )
