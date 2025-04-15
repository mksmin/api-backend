import uuid

from datetime import datetime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy import (
    String,
    DateTime,
    BigInteger,
    inspect,
)
from sqlalchemy.dialects.postgresql import UUID

from .mixins import IntIdMixin, TimestampsMixin
from .base import Base


class User(IntIdMixin, TimestampsMixin, Base):

    uuid = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )

    external_id_bid = mapped_column(
        BigInteger,
        nullable=True,
        comment="ID заявки из внешнего сервиса регистраций (например, Yandex.Form)",
    )
    external_date_bid: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=datetime.utcnow,
        comment="Дата регистрации пользователя во внешнем сервисе (например, Yandex.Form)",
    )

    # ФИО
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True, index=True)

    # Контакты
    email: Mapped[str] = mapped_column(String(250), nullable=True, index=True)
    mobile: Mapped[str] = mapped_column(String(60), nullable=True, index=True)
    tg_id = mapped_column(BigInteger, nullable=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)

    # Проживание и учеба
    citizenship: Mapped[str] = mapped_column(String(250), nullable=True)
    country: Mapped[str] = mapped_column(String(250), nullable=True)
    city: Mapped[str] = mapped_column(String(250), nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), nullable=True)
    study_place: Mapped[str] = mapped_column(
        String(500), nullable=True, comment="Учебное заведение"
    )
    grade_level: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Номер класса/курса"
    )

    # Прочее
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    sex: Mapped[str] = mapped_column(String(20), nullable=True, comment="Пол")

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
        return (
            f"<User("
            f"id={self.id}, "
            f"email={self.email}, "
            f"first_name={self.first_name}, "
            f"last_name={self.last_name}, "
            f"username={self.username},"
            f")>"
        )
