import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

logger = logging.getLogger(__name__)


class ProjectSchema(BaseModel):
    uuid: UUID = Field(..., alias="project_uuid")
    prj_name: str | None = None
    prj_description: str | None = None
    prj_owner: int

    @field_validator("uuid", mode="before")
    @classmethod
    def prevalidate(
        cls,
        value: Any,  # noqa: ANN401
    ) -> UUID:
        """Валидация UUID и преобразование строки"""
        try:
            if isinstance(value, UUID):
                return value
            return UUID(str(value))

        except (ValueError, AttributeError, TypeError) as e:
            msg_error = "Invalid UUID format"
            logger.exception("%s", msg_error)
            raise ValueError(msg_error) from e

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {"project_uuid": "123e4567-e89b-12d3-a456-426614174000"},
        },
    )


class ProjectRequestSchema(BaseModel):
    """
    Схема для создания проекта (клиент -> сервер)
    """

    name: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        alias="prj_name",
    )
    description: str | None = Field(
        None,
        max_length=200,
        alias="prj_description",
    )
    owner_id: int = Field(
        ...,
        alias="prj_owner",
        json_schema_extra={"example": 123456789},
    )
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "prj_name": "Test project",
                "prj_description": "Test project description",
                "prj_owner": 123456,
            },
        },
    )


class ProjectResponseSchema(BaseModel):
    """
    Схема для ответа от сервера (сервер -> клиент)
    """

    name: str | None = Field(None, alias="prj_name")
    description: str | None = Field(None, alias="prj_description")
    created_at: datetime
    uuid: UUID4 = Field(..., alias="uuid")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "prj_name": "Test project",
                "prj_description": "Test project description",
                "created_at": "2024-01-01T00:00:00",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
            },
        },
    )


class BaseMessageResponse(BaseModel):
    message: str
