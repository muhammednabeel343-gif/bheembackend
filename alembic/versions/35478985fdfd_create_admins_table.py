"""create admins table

Revision ID: 35478985fdfd
Revises: 001_create_app_schema
Create Date: 2026-06-03 19:53:30.205177
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "35478985fdfd"
down_revision: Union[str, Sequence[str], None] = "001_create_app_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )

    op.create_index("ix_admins_id", "admins", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_admins_id", table_name="admins")
    op.drop_table("admins")