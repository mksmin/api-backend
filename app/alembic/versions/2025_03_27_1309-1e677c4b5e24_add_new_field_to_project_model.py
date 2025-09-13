"""Add new field to Project model

Revision ID: 1e677c4b5e24
Revises: 2358086814ea
Create Date: 2025-03-27 13:09:30.978844

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e677c4b5e24"
down_revision: Union[str, None] = "2358086814ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "projects",
        sa.Column(
            "prj_owner",
            sa.BigInteger(),
            nullable=True,
            comment="tg_id пользователя",
        ),
    )
    op.add_column(
        "projects",
        sa.Column("prj_name", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("prj_description", sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "prj_owner")
    op.drop_column("projects", "prj_description")
    op.drop_column("projects", "prj_name")
