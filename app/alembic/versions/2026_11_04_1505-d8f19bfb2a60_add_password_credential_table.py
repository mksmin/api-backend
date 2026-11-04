"""add password credential table

Revision ID: d8f19bfb2a60
Revises: b76247aba816
Create Date: 2026-11-04 15:05:48.448495

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8f19bfb2a60"
down_revision: str | None = "b76247aba816"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "password_credentials",
        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True,
            ),
            server_default=sa.text(
                "now()",
            ),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "email_verified_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "password_hash",
            sa.Text(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(email) BETWEEN 1 AND 254",
            name=op.f(
                "ck_password_credentials_ck_password_credentials_email_length",
            ),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_password_credentials_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            name=op.f("pk_password_credentials"),
        ),
    )
    op.create_index(
        "uq_password_credential_email_lower",
        "password_credentials",
        [sa.literal_column("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_password_credential_email_lower",
        table_name="password_credentials",
    )
    op.drop_table("password_credentials")
