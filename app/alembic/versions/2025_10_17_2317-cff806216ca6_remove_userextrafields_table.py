"""remove UserExtraFields table

Revision ID: cff806216ca6
Revises: 09d43a83724d
Create Date: 2025-10-17 23:17:17.346915

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cff806216ca6"
down_revision: str | None = "09d43a83724d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("user_extra_fields")


def downgrade() -> None:
    op.create_table(
        "user_extra_fields",
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("extra_field_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("value", sa.VARCHAR(length=250), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["extra_field_id"],
            ["extra_fields.id"],
            name="fk_user_extra_fields_extra_field_id_extra_fields",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_extra_fields_user_id_users",
        ),
        sa.PrimaryKeyConstraint("user_id", name="pk_user_extra_fields"),
    )
