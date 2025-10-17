from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampsMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        server_default=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None]


class IntIdMixin:
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
