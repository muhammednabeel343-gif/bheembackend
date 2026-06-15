"""create rams table

Revision ID: 678901234abc
Revises: 5678901234ab
Create Date: 2026-06-03 21:16:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "678901234abc"
down_revision: Union[str, Sequence[str], None] = "5678901234ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rams",
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


def downgrade() -> None:
    op.drop_table("rams")