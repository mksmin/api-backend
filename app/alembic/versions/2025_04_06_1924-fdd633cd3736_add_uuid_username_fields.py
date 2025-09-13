"""Add uuid, username fields

Revision ID: fdd633cd3736
Revises: 11c6fc0e266c
Create Date: 2025-04-06 19:24:45.379879

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fdd633cd3736"
down_revision: str | None = "11c6fc0e266c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("uuid", sa.UUID(), nullable=True))
    op.add_column("users", sa.Column("username", sa.String(length=100), nullable=True))
    op.create_index(op.f("ix_users_tg_id"), "users", ["tg_id"], unique=False)
    op.create_unique_constraint(op.f("uq_users_uuid"), "users", ["uuid"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_users_uuid"), "users", type_="unique")
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.drop_column("users", "username")
    op.drop_column("users", "uuid")
