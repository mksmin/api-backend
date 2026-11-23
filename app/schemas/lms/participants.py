from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from pydantic import StringConstraints
from pydantic import field_validator

ParticipantFullName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=254,
    ),
]


class LMSParticipantsBase(BaseModel):
    full_name: ParticipantFullName
    email: EmailStr = Field(
        max_length=254,
    )

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class LMSParticipantsCreateSchema(LMSParticipantsBase): ...


class LMSParticipantsReadSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: UUID
    full_name: str
    email: str
    created_at: datetime
