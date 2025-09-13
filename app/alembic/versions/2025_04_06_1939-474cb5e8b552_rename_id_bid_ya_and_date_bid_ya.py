"""Rename id_bid_ya and date_bid_ya

Revision ID: 474cb5e8b552
Revises: 7593bd1c6813
Create Date: 2025-04-06 19:39:59.950017

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "474cb5e8b552"
down_revision: str | None = "7593bd1c6813"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "id_bid_ya",
        new_column_name="external_id_bid",
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        existing_comment="ID заявки из внешнего сервиса регистраций "
        "(например, Yandex.Form)",
    )
    op.alter_column(
        "users",
        "date_bid_ya",
        new_column_name="external_date_bid",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        existing_comment="Дата регистрации пользователя во внешнем сервисе "
        "(например, Yandex.Form)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Откат переименования
    op.alter_column(
        "users",
        "external_id_bid",
        new_column_name="id_bid_ya",
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        existing_comment="ID заявки из внешнего сервиса регистраций "
        "(например, Yandex.Form)",
    )
    op.alter_column(
        "users",
        "external_date_bid",
        new_column_name="date_bid_ya",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        existing_comment="Дата регистрации пользователя во внешнем сервисе "
        "(например, Yandex.Form)",
    )
