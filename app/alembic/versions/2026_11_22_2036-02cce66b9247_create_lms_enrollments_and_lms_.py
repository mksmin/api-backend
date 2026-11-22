"""create lms enrollments and lms participant tables

Revision ID: 02cce66b9247
Revises: 4f889a571c62
Create Date: 2026-11-22 20:36:31.564755

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "02cce66b9247"
down_revision: str | None = "4f889a571c62"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_lms_flows_project_id_id",
        "lms_flows",
        ["project_id", "id"],
    )
    op.create_table(
        "lms_participants",
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
            "full_name",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.Text(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "btrim(full_name) <> ''",
            name=op.f("ck_lms_participants_full_name_not_blank"),
        ),
        sa.CheckConstraint(
            "char_length(email) BETWEEN 1 AND 254",
            name=op.f("ck_lms_participants_email_length"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_lms_participants"),
        ),
        sa.UniqueConstraint(
            "uuid",
            name=op.f("uq_lms_participants_uuid"),
        ),
    )
    op.create_index(
        "uq_lms_participant_email_lower",
        "lms_participants",
        [
            sa.literal_column("lower(email)"),
        ],
        unique=True,
    )

    op.create_table(
        "lms_enrollments",
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
            "project_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "flow_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('active', 'excluded')",
            name=op.f("ck_lms_enrollments_status_values"),
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["lms_participants.id"],
            name=op.f("fk_lms_enrollments_participant_id_lms_participants"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "flow_id"],
            ["lms_flows.project_id", "lms_flows.id"],
            name="fk_lms_enrollments_project_flow",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_lms_enrollments_project_id_projects"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_lms_enrollments"),
        ),
        sa.UniqueConstraint(
            "project_id",
            "participant_id",
            name="uq_lms_enrollments_project_participant",
        ),
        sa.UniqueConstraint(
            "uuid",
            name=op.f("uq_lms_enrollments_uuid"),
        ),
    )


def downgrade() -> None:
    op.drop_table(
        "lms_enrollments",
    )
    op.drop_constraint(
        "uq_lms_flows_project_id_id",
        "lms_flows",
        type_="unique",
    )
    op.drop_index(
        "uq_lms_participant_email_lower",
        table_name="lms_participants",
    )
    op.drop_table(
        "lms_participants",
    )
