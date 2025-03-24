from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID

from app.core import logger


class ProjectSchema(BaseModel):
    uuid: UUID = Field(..., alias="project_uuid")

    @field_validator("uuid", mode="before")
    @classmethod
    def prevalidate(cls, value: Any) -> UUID:
        """Валидация UUID с преобразованием строки"""
        try:
            if isinstance(value, UUID):
                return value
            return UUID(str(value))

        except (ValueError, AttributeError, TypeError) as e:
            logger.error(f"Invalid UUID: {str(e)}")
            raise ValueError("Invalid UUID format") from e

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {"project_uuid": "123e4567-e89b-12d3-a456-426614174000"}
        },
    )
