"""create gpus table

Revision ID: 5678901234ab
Revises: 342d418545f1
Create Date: 2026-06-03 21:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5678901234ab"
down_revision: Union[str, Sequence[str], None] = "342d418545f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gpus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # No index on primary key 'id' needed; removed to avoid duplicate index on SQLite


def downgrade() -> None:
    op.drop_table("gpus")