import uuid

from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .mixins import IntIdMixin
from .mixins import TimestampsMixin


class User(IntIdMixin, TimestampsMixin, Base):
    uuid = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )
    first_name: Mapped[str | None] = mapped_column(
        String(150),
        comment="Имя",
    )
    last_name: Mapped[str | None] = mapped_column(
        String(150),
        index=True,
        comment="Фамилия",
    )
    tg_id = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="ID в Telegram",
        unique=True,
    )
    username: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Никнейм",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id})>"
