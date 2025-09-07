"""create table with extra_fields

Revision ID: 163de2bc2fd1
Revises: 5c487ccceaaa
Create Date: 2025-04-15 20:59:05.444440

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "163de2bc2fd1"
down_revision: Union[str, None] = "5c487ccceaaa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "extra_fields",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_name", sa.String(length=250), nullable=False),
        sa.Column("field_type", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_extra_fields")),
        sa.UniqueConstraint("field_name", name=op.f("uq_extra_fields_field_name")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("extra_fields")
