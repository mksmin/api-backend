from typing import Annotated
from uuid import UUID

from annotated_types import Len, MaxLen
from pydantic import BaseModel, ConfigDict

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


class ProjectCreateModel(ProjectBase):
    owner_id: int
    parent_id: int | None = None


class ProjectCreateSchema(ProjectBase):
    owner_uuid: UUID


class ProjectReadSchema(ProjectBase):
    owner_uuid: UUID
    parent_id: int | None = None
