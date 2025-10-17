"""remove Roles table

Revision ID: 54676d53a7bb
Revises: fefa2a765300
Create Date: 2025-10-17 23:20:47.193116

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "54676d53a7bb"
down_revision: str | None = "fefa2a765300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("roles")


def downgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column(
            "description",
            sa.VARCHAR(length=200),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
