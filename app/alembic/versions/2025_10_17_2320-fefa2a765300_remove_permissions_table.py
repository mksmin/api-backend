"""remove Permissions table

Revision ID: fefa2a765300
Revises: 69ea416f3ec0
Create Date: 2025-10-17 23:20:15.397951

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fefa2a765300"
down_revision: str | None = "69ea416f3ec0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("permissions")


def downgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("code", sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column(
            "description",
            sa.VARCHAR(length=200),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
