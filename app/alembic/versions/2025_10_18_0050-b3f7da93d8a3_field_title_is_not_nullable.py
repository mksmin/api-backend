"""field title is not nullable

Revision ID: b3f7da93d8a3
Revises: 2da95c7e793a
Create Date: 2025-10-18 00:50:59.545604

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3f7da93d8a3"
down_revision: str | None = "2da95c7e793a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "projects",
        "title",
        existing_type=sa.VARCHAR(length=50),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "projects",
        "title",
        existing_type=sa.VARCHAR(length=50),
        nullable=True,
    )
