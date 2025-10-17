import uuid

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    inspect,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
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

    first_name: Mapped[str] = mapped_column(String(150), nullable=True, comment="Имя")
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

    extra_fields = relationship("UserExtraField", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")

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


class ExtraField(IntIdMixin, Base):
    field_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    field_type: Mapped[str] = mapped_column(String(30), nullable=False)

    values = relationship("UserExtraField", back_populates="extra_field")


class UserExtraField(Base):
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        primary_key=True,
    )
    extra_field_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("extra_fields.id"),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(String(250), nullable=True)

    user = relationship("User", back_populates="extra_fields")
    extra_field = relationship("ExtraField", back_populates="values")


class Role(IntIdMixin, Base):
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
    )


class Permission(IntIdMixin, Base):
    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )  # e.g. "can_edit_profiles"
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )


class UserRole(Base):
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id"),
        primary_key=True,
    )


class RolePermission(Base):
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("permissions.id"),
        primary_key=True,
    )
