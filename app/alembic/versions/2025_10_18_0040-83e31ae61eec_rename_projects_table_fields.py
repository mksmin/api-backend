"""rename projects table fields

Revision ID: 83e31ae61eec
Revises: 5fee64355616
Create Date: 2025-10-18 00:40:19.065164

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "83e31ae61eec"
down_revision: str | None = "5fee64355616"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "projects",
        "prj_name",
        new_column_name="title",
        existing_type=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "projects",
        "prj_description",
        new_column_name="description",
        existing_type=sa.String(length=200),
        existing_nullable=True,
    )
    op.alter_column(
        "projects",
        "prj_owner",
        new_column_name="owner_id",
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        existing_comment="id пользователя",
    )


def downgrade() -> None:
    op.alter_column(
        "projects",
        "title",
        new_column_name="prj_name",
        existing_type=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "projects",
        "description",
        new_column_name="prj_description",
        existing_type=sa.String(length=200),
        existing_nullable=True,
    )
    op.alter_column(
        "projects",
        "owner_id",
        new_column_name="prj_owner",
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        existing_comment="id пользователя",
    )
