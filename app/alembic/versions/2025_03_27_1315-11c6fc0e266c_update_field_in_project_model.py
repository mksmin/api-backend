"""Update field in Project model

Revision ID: 11c6fc0e266c
Revises: 1e677c4b5e24
Create Date: 2025-03-27 13:15:06.973001

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "11c6fc0e266c"
down_revision: str | None = "1e677c4b5e24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "projects",
        "prj_owner",
        existing_type=sa.BIGINT(),
        nullable=False,
        existing_comment="tg_id пользователя",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "projects",
        "prj_owner",
        existing_type=sa.BIGINT(),
        nullable=True,
        existing_comment="tg_id пользователя",
    )
