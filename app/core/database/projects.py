import uuid

from sqlalchemy import UUID, String, BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.database import Base
from app.core.database.mixins import IntIdMixin, TimestampsMixin


class Project(IntIdMixin, TimestampsMixin, Base):
    uuid = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )
    prj_name: Mapped[str] = mapped_column(String(50), nullable=True)
    prj_description: Mapped[str] = mapped_column(String(200), nullable=True)
    prj_owner = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True, comment="id пользователя")
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('projects.id'), nullable=True,
                                           comment="id родительского проекта")

    parent: Mapped["Project"] = relationship("Project", remote_side='Project.id', backref="subprojects", lazy="joined")
