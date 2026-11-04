import uuid
from datetime import UTC
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
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


class PasswordCredential(
    Base,
):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
        default=None,
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "char_length(email) BETWEEN 1 AND 254",
            name="ck_password_credentials_email_length",
        ),
    )


Index(
    "uq_password_credential_email_lower",
    func.lower(
        PasswordCredential.__table__.c.email,
    ),
    unique=True,
)
