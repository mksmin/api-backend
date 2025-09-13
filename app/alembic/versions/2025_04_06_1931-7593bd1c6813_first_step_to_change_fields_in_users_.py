"""First step to change fields in users table

Revision ID: 7593bd1c6813
Revises: fdd633cd3736
Create Date: 2025-04-06 19:31:41.329155

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7593bd1c6813"
down_revision: Union[str, None] = "fdd633cd3736"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "id_bid_ya",
        existing_type=sa.BIGINT(),
        nullable=True,
        comment="ID заявки из внешнего сервиса регистраций (например, Yandex.Form)",
        existing_comment="ID заявки из внешнего сервиса регистраций (Yandex.Form)",
    )
    op.alter_column(
        "users",
        "date_bid_ya",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        comment="Дата регистрации пользователя во внешнем сервисе (например, Yandex.Form)",
        existing_comment="Дата регистрации пользователя во внешнем сервисе (Yandex.Form)",
    )
    op.drop_index("ix_users_id_bid_ya", table_name="users")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index("ix_users_id_bid_ya", "users", ["id_bid_ya"], unique=True)
    op.alter_column(
        "users",
        "date_bid_ya",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        comment="Дата регистрации пользователя во внешнем сервисе (Yandex.Form)",
        existing_comment="Дата регистрации пользователя во внешнем сервисе (например, Yandex.Form)",
    )
    op.alter_column(
        "users",
        "id_bid_ya",
        existing_type=sa.BIGINT(),
        nullable=False,
        comment="ID заявки из внешнего сервиса регистраций (Yandex.Form)",
        existing_comment="ID заявки из внешнего сервиса регистраций (например, Yandex.Form)",
    )
