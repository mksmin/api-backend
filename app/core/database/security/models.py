from datetime import datetime
from sqlalchemy import String, Column, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, IntIdMixin, TimestampsMixin


class APIKey(IntIdMixin, TimestampsMixin, Base):
    __tablename__ = "api_keys"

    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
