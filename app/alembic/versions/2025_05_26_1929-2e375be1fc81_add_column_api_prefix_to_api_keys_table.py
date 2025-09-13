"""add column api_prefix to api_keys table

Revision ID: 2e375be1fc81
Revises: 6cf4a8e5a337
Create Date: 2025-05-26 19:29:14.667922

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e375be1fc81"
down_revision: str | None = "6cf4a8e5a337"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "api_keys",
        sa.Column("key_prefix", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("api_keys", "key_prefix")
