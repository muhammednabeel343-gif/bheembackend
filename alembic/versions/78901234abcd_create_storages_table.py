"""create storages table

Revision ID: 78901234abcd
Revises: 678901234abc
Create Date: 2026-06-03 21:17:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "78901234abcd"
down_revision: Union[str, Sequence[str], None] = "678901234abc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "storages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("size"),
    )

    op.create_index("ix_storages_id", "storages", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_storages_id", table_name="storages")
    op.drop_table("storages")