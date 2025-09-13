"""Create FK in Projects table

Revision ID: 471d42f906f5
Revises: a6c41502fc9e
Create Date: 2025-04-27 20:31:47.626156

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "471d42f906f5"
down_revision: str | None = "a6c41502fc9e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "projects",
        "prj_owner",
        existing_type=sa.BIGINT(),
        comment="id пользователя",
        existing_comment="tg_id пользователя",
        existing_nullable=False,
    )
    op.create_foreign_key(
        op.f("fk_projects_prj_owner_users"),
        "projects",
        "users",
        ["prj_owner"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_projects_prj_owner_users"),
        "projects",
        type_="foreignkey",
    )
    op.alter_column(
        "projects",
        "prj_owner",
        existing_type=sa.BIGINT(),
        comment="tg_id пользователя",
        existing_comment="id пользователя",
        existing_nullable=False,
    )
