"""Create users table

Revision ID: 1520d1beeddc
Revises: 3e8ce9eeaf9a
Create Date: 2025-03-20 19:55:38.881955

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1520d1beeddc"
down_revision: Union[str, None] = "3e8ce9eeaf9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "id_bid_ya",
            sa.Integer(),
            nullable=False,
            comment="ID заявки из внешнего сервиса регистраций (Yandex.Form)",
        ),
        sa.Column(
            "date_bid_ya",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Дата регистрации пользователя во внешнем сервисе (Yandex.Form)",
        ),
        sa.Column("first_name", sa.String(length=150), nullable=True),
        sa.Column("middle_name", sa.String(length=150), nullable=True),
        sa.Column("last_name", sa.String(length=150), nullable=True),
        sa.Column("email", sa.String(length=250), nullable=True),
        sa.Column("mobile", sa.String(length=60), nullable=True),
        sa.Column("tg_id", sa.BigInteger(), nullable=True),
        sa.Column("citizenship", sa.String(length=250), nullable=True),
        sa.Column("country", sa.String(length=250), nullable=True),
        sa.Column("city", sa.String(length=250), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=True),
        sa.Column(
            "study_place",
            sa.String(length=500),
            nullable=True,
            comment="Учебное заведение",
        ),
        sa.Column(
            "grade_level",
            sa.String(length=100),
            nullable=True,
            comment="Номер класса/курса",
        ),
        sa.Column("birth_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sex", sa.String(length=20), nullable=True, comment="Пол"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(
        op.f("ix_users_id_bid_ya"), "users", ["id_bid_ya"], unique=True
    )
    op.create_index(
        op.f("ix_users_last_name"), "users", ["last_name"], unique=False
    )
    op.create_index(op.f("ix_users_mobile"), "users", ["mobile"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_mobile"), table_name="users")
    op.drop_index(op.f("ix_users_last_name"), table_name="users")
    op.drop_index(op.f("ix_users_id_bid_ya"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
