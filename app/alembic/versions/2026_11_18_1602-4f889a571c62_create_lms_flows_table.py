"""create lms flows table

Revision ID: 4f889a571c62
Revises: 160d16f5ad87
Create Date: 2026-11-18 16:02:45.197931

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f889a571c62"
down_revision: str | None = "160d16f5ad87"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "lms_flows",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=False,
            comment="ID Проекта",
        ),
        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(title) BETWEEN 1 AND 254 AND btrim(title) <> ''",
            name=op.f("ck_lms_flows_title_length"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_lms_flows_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_lms_flows"),
        ),
        sa.UniqueConstraint(
            "uuid",
            name=op.f("uq_lms_flows_uuid"),
        ),
    )
    op.create_index(
        "uq_lms_flows_project_id_title_active",
        "lms_flows",
        ["project_id", sa.literal_column("lower(title)")],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_lms_flows_project_id_title_active",
        table_name="lms_flows",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.drop_table("lms_flows")
