from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from core.database import (
    Base,
    IntIdMixin,
    TimestampsMixin,
)

if TYPE_CHECKING:
    from core.database.projects import Project


class APIKey(IntIdMixin, TimestampsMixin, Base):
    __tablename__ = "api_keys"

    key_prefix: Mapped[str] = mapped_column(String(16), nullable=True)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False, index=True
    )

    project: Mapped["Project"] = relationship("Project", back_populates="api_keys")
