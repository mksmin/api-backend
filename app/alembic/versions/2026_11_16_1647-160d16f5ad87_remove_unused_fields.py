"""Remove unused fields

Revision ID: 160d16f5ad87
Revises: d8f19bfb2a60
Create Date: 2026-11-16 16:47:13.366304

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "160d16f5ad87"
down_revision: str | None = "d8f19bfb2a60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        type_="foreignkey",
    )
    op.drop_column(
        "projects",
        "parent_id",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "projects",
        sa.Column(
            "parent_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
            comment="id родительского проекта",
        ),
    )
    op.create_foreign_key(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        "projects",
        ["parent_id"],
        ["id"],
    )
