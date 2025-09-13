"""Create projects table

Revision ID: 927ecaa7fb69
Revises: 1520d1beeddc
Create Date: 2025-03-20 19:59:43.177447

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "927ecaa7fb69"
down_revision: Union[str, None] = "1520d1beeddc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.UniqueConstraint("uuid", name=op.f("uq_projects_uuid")),
    )
    op.add_column(
        "users",
        sa.Column("project_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "track",
            sa.String(length=250),
            nullable=True,
            comment="Название компетенции/трека",
        ),
    )
    op.create_foreign_key(
        op.f("fk_users_project_id_projects"),
        "users",
        "projects",
        ["project_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_users_project_id_projects"),
        "users",
        type_="foreignkey",
    )
    op.drop_column("users", "track")
    op.drop_column("users", "project_id")
    op.drop_table("projects")
