"""Remove track and project_id in users table

Revision ID: e9300def0c06
Revises: 474cb5e8b552
Create Date: 2025-04-06 19:49:55.654998

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e9300def0c06"
down_revision: str | None = "474cb5e8b552"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("fk_users_project_id_projects", "users", type_="foreignkey")
    op.drop_column("users", "project_id")
    op.drop_column("users", "track")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "track",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=True,
            comment="Название компетенции/трека",
        ),
    )
    op.add_column(
        "users",
        sa.Column("project_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "fk_users_project_id_projects",
        "users",
        "projects",
        ["project_id"],
        ["id"],
    )
