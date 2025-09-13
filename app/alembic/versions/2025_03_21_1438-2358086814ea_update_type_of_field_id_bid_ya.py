"""Update type of field id_bid_ya

Revision ID: 2358086814ea
Revises: 927ecaa7fb69
Create Date: 2025-03-21 14:38:47.225974

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2358086814ea"
down_revision: Union[str, None] = "927ecaa7fb69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "id_bid_ya",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_comment="ID заявки из внешнего сервиса регистраций (Yandex.Form)",
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "id_bid_ya",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_comment="ID заявки из внешнего сервиса регистраций (Yandex.Form)",
        existing_nullable=False,
    )
