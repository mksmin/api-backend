"""Update nullable in users.uuid. Now is False

Revision ID: 5c487ccceaaa
Revises: e9300def0c06
Create Date: 2025-04-06 20:11:27.667869

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c487ccceaaa"
down_revision: str | None = "e9300def0c06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "uuid", existing_type=sa.UUID(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("users", "uuid", existing_type=sa.UUID(), nullable=True)
