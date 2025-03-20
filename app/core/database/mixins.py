from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampsMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(default=None, server_default=None, nullable=True)


class IntIdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
