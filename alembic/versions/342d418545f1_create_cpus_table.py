"""create cpus table

Revision ID: 342d418545f1
Revises: 35478985fdfd
Create Date: 2026-06-03 20:42:01.726063
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "342d418545f1"
down_revision: Union[str, Sequence[str], None] = "35478985fdfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cpus",
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

    op.create_index(
        "ix_cpus_id",
        "cpus",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cpus_id",
        table_name="cpus",
    )

    op.drop_table("cpus")