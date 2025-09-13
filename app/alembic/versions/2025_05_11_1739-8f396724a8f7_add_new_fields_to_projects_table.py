"""add new fields to projects table

Revision ID: 8f396724a8f7
Revises: 471d42f906f5
Create Date: 2025-05-11 17:39:09.750427

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f396724a8f7"
down_revision: Union[str, None] = "471d42f906f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "projects",
        sa.Column(
            "parent_id",
            sa.BigInteger(),
            nullable=True,
            comment="id родительского проекта",
        ),
    )
    op.alter_column(
        "projects",
        "prj_owner",
        existing_type=sa.BIGINT(),
        nullable=True,
        existing_comment="id пользователя",
    )
    op.create_foreign_key(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        "projects",
        ["parent_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        type_="foreignkey",
    )
    op.alter_column(
        "projects",
        "prj_owner",
        existing_type=sa.BIGINT(),
        nullable=False,
        existing_comment="id пользователя",
    )
    op.drop_column("projects", "parent_id")
