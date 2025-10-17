import uuid

from sqlalchemy import (
    UUID,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from core.database import Base
from core.database.mixins import IntIdMixin, TimestampsMixin


class Project(IntIdMixin, TimestampsMixin, Base):
    uuid = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(200))
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        comment="id пользователя",
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"),
        comment="id родительского проекта",
    )

    parent: Mapped["Project"] = relationship(
        "Project",
        remote_side="Project.id",
        backref="subprojects",
        lazy="joined",
    )
    api_keys = relationship("APIKey", back_populates="project")
