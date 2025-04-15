"""create table with user_extra_fields

Revision ID: 9036f1f30c3b
Revises: 163de2bc2fd1
Create Date: 2025-04-15 21:00:59.717292

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9036f1f30c3b"
down_revision: Union[str, None] = "163de2bc2fd1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_extra_fields",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("extra_field_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=250), nullable=True),
        sa.ForeignKeyConstraint(
            ["extra_field_id"],
            ["extra_fields.id"],
            name=op.f("fk_user_extra_fields_extra_field_id_extra_fields"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_extra_fields_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_extra_fields")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_extra_fields")
