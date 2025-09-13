"""Update nullable in users.uuid. Now is False

Revision ID: 5c487ccceaaa
Revises: e9300def0c06
Create Date: 2025-04-06 20:11:27.667869

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c487ccceaaa"
down_revision: Union[str, None] = "e9300def0c06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "uuid", existing_type=sa.UUID(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("users", "uuid", existing_type=sa.UUID(), nullable=True)
