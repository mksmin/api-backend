import uuid

from sqlalchemy import UUID
from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from core.database.base import Base
from core.database.mixins import IntIdMixin
from core.database.mixins import TimestampsMixin


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
    )
