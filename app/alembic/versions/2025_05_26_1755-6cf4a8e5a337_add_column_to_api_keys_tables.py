"""add column to api keys tables

Revision ID: 6cf4a8e5a337
Revises: 2749b12e6557
Create Date: 2025-05-26 17:55:43.855517

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6cf4a8e5a337"
down_revision: str | None = "2749b12e6557"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("api_keys", sa.Column("project_id", sa.Integer(), nullable=False))
    op.create_index(
        op.f("ix_api_keys_project_id"),
        "api_keys",
        ["project_id"],
        unique=False,
    )
    op.create_foreign_key(
        op.f("fk_api_keys_project_id_projects"),
        "api_keys",
        "projects",
        ["project_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_api_keys_project_id_projects"),
        "api_keys",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_api_keys_project_id"), table_name="api_keys")
    op.drop_column("api_keys", "project_id")
