from datetime import datetime
from typing import Annotated
from typing import Any
from uuid import UUID

from annotated_types import Len
from annotated_types import MaxLen
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import model_validator
from pydantic_core.core_schema import ValidationInfo

DESCRIPTION_MAX_LENGTH = 200
TITLE_MAX_LENGTH = 50

TitleString = Annotated[
    str,
    Len(
        min_length=1,
        max_length=TITLE_MAX_LENGTH,
    ),
]
DescriptionString = Annotated[
    str,
    MaxLen(DESCRIPTION_MAX_LENGTH),
]


class ProjectBase(BaseModel):
    """
    Базовая схема для модели проекта
    """

    title: TitleString
    description: DescriptionString = ""

    model_config = ConfigDict(from_attributes=True)

    @field_validator("title", mode="after")
    @classmethod
    def validate_title(cls, v: str) -> str:
        return v.strip()


class ProjectCreateModel(ProjectBase):
    owner_id: int
    parent_id: int | None = None


class ProjectCreateSchema(ProjectBase):
    """
    Схема для создания проекта
    """

    # owner_uuid: UUID


class ProjectReadValidation(ProjectBase):
    @model_validator(
        mode="before",
    )
    @classmethod
    def fill_owner_uuid(
        cls,
        v: dict[str, Any],
        info: ValidationInfo,
    ) -> dict[str, Any]:
        if not isinstance(v, dict):
            v = v.__dict__

        if "owner_uuid" not in v and isinstance(info.context, dict):
            v["owner_uuid"] = info.context.get("owner_uuid")
        return v


class ProjectReadSchema(ProjectReadValidation):
    uuid: UUID
    created_at: datetime
    owner_uuid: UUID
    parent_id: int | None = None


class ProjectSchema(ProjectReadValidation):
    id: int
    uuid: UUID
    created_at: datetime
    deleted_at: datetime | None = None
    owner_id: int
    owner_uuid: UUID | None = None
    parent_id: int | None = None
