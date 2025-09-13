"""Add comments to field in users table

Revision ID: a1f1d1d48ba6
Revises: 9036f1f30c3b
Create Date: 2025-04-15 21:11:59.988265

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1f1d1d48ba6"
down_revision: Union[str, None] = "9036f1f30c3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "first_name",
        existing_type=sa.VARCHAR(length=150),
        comment="Имя",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "middle_name",
        existing_type=sa.VARCHAR(length=150),
        comment="Отчество",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "last_name",
        existing_type=sa.VARCHAR(length=150),
        comment="Фамилия",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(length=250),
        comment="Email",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "mobile",
        existing_type=sa.VARCHAR(length=60),
        comment="Телефон",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "tg_id",
        existing_type=sa.BIGINT(),
        comment="ID в Telegram",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=100),
        comment="Никнейм",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "citizenship",
        existing_type=sa.VARCHAR(length=250),
        comment="Гражданство",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "country",
        existing_type=sa.VARCHAR(length=250),
        comment="Страна",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "city",
        existing_type=sa.VARCHAR(length=250),
        comment="Город",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "timezone",
        existing_type=sa.VARCHAR(length=100),
        comment="Часовой пояс",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "birth_date",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment="Дата рождения",
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "birth_date",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment=None,
        existing_comment="Дата рождения",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "timezone",
        existing_type=sa.VARCHAR(length=100),
        comment=None,
        existing_comment="Часовой пояс",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "city",
        existing_type=sa.VARCHAR(length=250),
        comment=None,
        existing_comment="Город",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "country",
        existing_type=sa.VARCHAR(length=250),
        comment=None,
        existing_comment="Страна",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "citizenship",
        existing_type=sa.VARCHAR(length=250),
        comment=None,
        existing_comment="Гражданство",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=100),
        comment=None,
        existing_comment="Никнейм",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "tg_id",
        existing_type=sa.BIGINT(),
        comment=None,
        existing_comment="ID в Telegram",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "mobile",
        existing_type=sa.VARCHAR(length=60),
        comment=None,
        existing_comment="Телефон",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(length=250),
        comment=None,
        existing_comment="Email",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "last_name",
        existing_type=sa.VARCHAR(length=150),
        comment=None,
        existing_comment="Фамилия",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "middle_name",
        existing_type=sa.VARCHAR(length=150),
        comment=None,
        existing_comment="Отчество",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "first_name",
        existing_type=sa.VARCHAR(length=150),
        comment=None,
        existing_comment="Имя",
        existing_nullable=True,
    )
