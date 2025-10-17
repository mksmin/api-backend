"""remove fk from project table

Revision ID: 5fee64355616
Revises: 54676d53a7bb
Create Date: 2025-10-18 00:38:42.589576

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5fee64355616"
down_revision: str | None = "54676d53a7bb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_projects_prj_owner_users"),
        "projects",
        type_="foreignkey",
    )


def downgrade() -> None:
    op.create_foreign_key(
        op.f("fk_projects_prj_owner_users"),
        "projects",
        "users",
        ["prj_owner"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_projects_parent_id_projects"),
        "projects",
        "projects",
        ["parent_id"],
        ["id"],
    )
