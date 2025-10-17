"""remove ExtraFields table

Revision ID: eb700c427651
Revises: cff806216ca6
Create Date: 2025-10-17 23:17:55.118942

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eb700c427651"
down_revision: str | None = "cff806216ca6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("extra_fields")


def downgrade() -> None:
    op.create_table(
        "extra_fields",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "field_name",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "field_type",
            sa.VARCHAR(length=30),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_extra_fields"),
        sa.UniqueConstraint("field_name", name="uq_extra_fields_field_name"),
    )
