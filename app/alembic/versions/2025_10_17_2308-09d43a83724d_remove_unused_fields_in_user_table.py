"""remove unused fields in user table

Revision ID: 09d43a83724d
Revises: 2e375be1fc81
Create Date: 2025-10-17 23:08:36.853950

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "09d43a83724d"
down_revision: str | None = "2e375be1fc81"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_mobile", table_name="users")
    op.drop_column("users", "external_date_bid")
    op.drop_column("users", "mobile")
    op.drop_column("users", "external_id_bid")
    op.drop_column("users", "birth_date")
    op.drop_column("users", "middle_name")
    op.drop_column("users", "sex")
    op.drop_column("users", "country")
    op.drop_column("users", "city")
    op.drop_column("users", "email")
    op.drop_column("users", "grade_level")
    op.drop_column("users", "timezone")
    op.drop_column("users", "study_place")
    op.drop_column("users", "citizenship")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "citizenship",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=True,
            comment="Гражданство",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "study_place",
            sa.VARCHAR(length=500),
            autoincrement=False,
            nullable=True,
            comment="Учебное заведение",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "timezone",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
            comment="Часовой пояс",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "grade_level",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
            comment="Номер класса/курса",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "email",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=True,
            comment="Email",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "city",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=True,
            comment="Город",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "country",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=True,
            comment="Страна",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "sex",
            sa.VARCHAR(length=20),
            autoincrement=False,
            nullable=True,
            comment="Пол",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "middle_name",
            sa.VARCHAR(length=150),
            autoincrement=False,
            nullable=True,
            comment="Отчество",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "birth_date",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
            comment="Дата рождения",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "external_id_bid",
            sa.BIGINT(),
            autoincrement=False,
            nullable=True,
            comment="ID заявки из внешнего сервиса регистраций "
            "(например, Yandex.Form)",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "mobile",
            sa.VARCHAR(length=60),
            autoincrement=False,
            nullable=True,
            comment="Телефон",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "external_date_bid",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
            comment="Дата регистрации пользователя во внешнем сервисе "
            "(например, Yandex.Form)",
        ),
    )
    op.create_index("ix_users_mobile", "users", ["mobile"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)
