import uuid

from sqlalchemy import (
    BigInteger,
    String,
    inspect,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .base import Base
from .mixins import IntIdMixin, TimestampsMixin


class User(IntIdMixin, TimestampsMixin, Base):

    uuid = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(150),
        nullable=True,
        comment="Имя",
    )
    last_name: Mapped[str] = mapped_column(
        String(150),
        nullable=True,
        index=True,
        comment="Фамилия",
    )

    tg_id = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="ID в Telegram",
    )
    username: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Никнейм",
    )

    @classmethod
    def get_model_fields(
        cls,
        exclude_primary_key: bool = True,
        exclude_foreign_keys: bool = True,
    ) -> list[str]:
        inspector = inspect(cls)
        columns = []

        for column in inspector.columns:
            if exclude_primary_key and column.primary_key:
                continue
            if exclude_foreign_keys and column.foreign_keys:
                continue

            columns.append(column.name)

        return columns

    def __repr__(self) -> str:
        return f"<User(id={self.id})>"
