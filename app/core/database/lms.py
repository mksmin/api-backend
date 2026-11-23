import uuid
from typing import Literal

from sqlalchemy import UUID
from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from core.database.base import Base
from core.database.mixins import IntIdMixin
from core.database.mixins import TimestampsMixin
from core.database.mixins import UUIDMixin


class LMSFlow(
    IntIdMixin,
    TimestampsMixin,
    Base,
):
    __tablename__ = "lms_flows"

    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(
            as_uuid=True,
        ),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        comment="ID Проекта",
    )
    title: Mapped[str] = mapped_column(
        Text,
    )

    project = relationship(
        "Project",
        back_populates="prj_flows",
    )

    __table_args__ = (
        CheckConstraint(
            "char_length(title) BETWEEN 1 AND 254 AND btrim(title) <> ''",
            name="title_length",
        ),
        Index(
            "uq_lms_flows_project_id_title_active",
            "project_id",
            func.lower(title),
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        UniqueConstraint(
            "project_id",
            "id",
            name="uq_lms_flows_project_id_id",
        ),
    )


class LMSParticipant(
    IntIdMixin,
    UUIDMixin,
    TimestampsMixin,
    Base,
):
    __tablename__ = "lms_participants"

    full_name: Mapped[str] = mapped_column(
        Text,
    )
    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "char_length(email) BETWEEN 1 AND 254",
            name="email_length",
        ),
        CheckConstraint(
            "btrim(full_name) <> ''",
            name="full_name_not_blank",
        ),
    )


Index(
    "uq_lms_participant_email_lower",
    func.lower(
        LMSParticipant.__table__.c.email,
    ),
    unique=True,
)


class LMSEnrollment(
    IntIdMixin,
    UUIDMixin,
    TimestampsMixin,
    Base,
):
    __tablename__ = "lms_enrollments"

    project_id: Mapped[int] = mapped_column(
        ForeignKey(
            "projects.id",
        ),
        nullable=False,
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lms_participants.id",
        ),
        nullable=False,
    )
    flow_id: Mapped[int] = mapped_column(
        nullable=False,
    )
    status: Mapped[
        Literal[
            "active",
            "excluded",
        ]
    ] = mapped_column(
        Text,
        nullable=False,
        default="active",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'excluded')",
            name="status_values",
        ),
        UniqueConstraint(
            "project_id",
            "participant_id",
            name="uq_lms_enrollments_project_participant",
        ),
        ForeignKeyConstraint(
            [
                "project_id",
                "flow_id",
            ],
            [
                "lms_flows.project_id",
                "lms_flows.id",
            ],
            name="fk_lms_enrollments_project_flow",
        ),
    )
