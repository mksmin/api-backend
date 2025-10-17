"""create fk for projects table

Revision ID: 2da95c7e793a
Revises: 83e31ae61eec
Create Date: 2025-10-18 00:47:15.803579

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2da95c7e793a"
down_revision: str | None = "83e31ae61eec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "projects",
        "owner_id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        nullable=False,
        existing_comment="id пользователя",
    )
    op.alter_column(
        "projects",
        "parent_id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_comment="id родительского проекта",
        existing_nullable=True,
    )
    op.create_foreign_key(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        "projects",
        ["parent_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_projects_owner_id_users"),
        "projects",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_projects_owner_id_users"),
        "projects",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        type_="foreignkey",
    )
    op.alter_column(
        "projects",
        "parent_id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_comment="id родительского проекта",
        existing_nullable=True,
    )
    op.alter_column(
        "projects",
        "owner_id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        nullable=True,
        existing_comment="id пользователя",
    )
