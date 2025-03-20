import uuid

from datetime import datetime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID

from .mixins import IntIdMixin, TimestampsMixin
from .base import Base


class User(IntIdMixin, TimestampsMixin, Base):
    id_bid_ya: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        comment="ID заявки из внешнего сервиса регистраций (Yandex.Form)",
        index=True
    )
    date_bid_ya: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Дата регистрации пользователя во внешнем сервисе (Yandex.Form)"
    )

    # ФИО
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True, index=True)

    # Контакты
    email: Mapped[str] = mapped_column(String(250), nullable=True, index=True)
    mobile: Mapped[str] = mapped_column(String(60), nullable=True, index=True)
    tg_id = mapped_column(BigInteger, nullable=True)

    # Проживание и учеба
    citizenship: Mapped[str] = mapped_column(String(250), nullable=True)
    country: Mapped[str] = mapped_column(String(250), nullable=True)
    city: Mapped[str] = mapped_column(String(250), nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), nullable=True)
    study_place: Mapped[str] = mapped_column(String(500), nullable=True, comment="Учебное заведение")
    grade_level: Mapped[str] = mapped_column(String(100), nullable=True, comment="Номер класса/курса")

    # Прочее
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    sex: Mapped[str] = mapped_column(String(20), nullable=True, comment="Пол")

    # Проект
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=True, unique=False)
    track: Mapped[str] = mapped_column(String(250), nullable=True, comment="Название компетенции/трека")

    prj = relationship('Project', back_populates='user', uselist=False)


class Project(IntIdMixin, TimestampsMixin, Base):
    uuid = mapped_column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, unique=True)

    user = relationship('User', back_populates='prj')
