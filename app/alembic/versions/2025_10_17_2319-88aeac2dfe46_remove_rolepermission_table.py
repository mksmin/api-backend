"""remove RolePermission table

Revision ID: 88aeac2dfe46
Revises: eb700c427651
Create Date: 2025-10-17 23:19:00.495011

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "88aeac2dfe46"
down_revision: str | None = "eb700c427651"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("role_permissions")


def downgrade() -> None:
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("permission_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_permissions_permission_id_permissions",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_role_permissions_role_id_roles",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name="pk_role_permissions"),
    )
