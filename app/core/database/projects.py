import uuid

from sqlalchemy import UUID
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from core.database import Base
from core.database.mixins import IntIdMixin
from core.database.mixins import TimestampsMixin


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

    api_keys = relationship(
        "APIKey",
        back_populates="project",
    )
    prj_flows = relationship(
        "LMSFlow",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
