from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import StringConstraints

FlowTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=254,
    ),
]


class LMSFlowsBase(
    BaseModel,
):
    title: FlowTitle


class LMSFlowsCreateSchema(
    LMSFlowsBase,
):
    pass


class LMSFlowsUpdateSchema(
    LMSFlowsBase,
):
    pass


class LMSFlowsCreateModel(
    LMSFlowsCreateSchema,
):
    project_id: int


class LMSFlowsReadSchema(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: UUID
    project_id: int
    title: str
    created_at: datetime
