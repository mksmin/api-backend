from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict

from schemas.lms.participants import LMSParticipantsCreateSchema


class LMSEnrollmentsCreateSchema(
    LMSParticipantsCreateSchema,
):
    flow_uuid: UUID


class LMSEnrollmentsCreateModel(
    BaseModel,
):
    project_id: int
    participant_id: int
    flow_id: int


class LMSEnrollmentsReadSchema(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: UUID
    project_uuid: UUID
    participant_uuid: UUID
    full_name: str
    email: str
    flow_uuid: UUID
    flow_title: str
    status: Literal[
        "active",
        "excluded",
    ]
    created_at: datetime
