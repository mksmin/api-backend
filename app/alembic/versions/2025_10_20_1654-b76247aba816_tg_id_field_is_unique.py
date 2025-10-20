"""tg id field is unique

Revision ID: b76247aba816
Revises: b3f7da93d8a3
Create Date: 2025-10-20 16:54:54.082708

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b76247aba816"
down_revision: str | None = "b3f7da93d8a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.create_index(
        op.f("ix_users_tg_id"),
        "users",
        ["tg_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.create_index(
        op.f("ix_users_tg_id"),
        "users",
        ["tg_id"],
        unique=False,
    )
