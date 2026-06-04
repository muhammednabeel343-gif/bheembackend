"""add storage_gb column to games

Revision ID: add_storage_gb_column
Revises: 89012345abcd
Create Date: 2026-06-04 00:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_storage_gb_column"
down_revision: Union[str, Sequence[str], None] = "89012345abcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('fk_games_storage', 'games', type_='foreignkey')
    op.drop_column('games', 'storage_id')
    op.add_column('games', sa.Column('storage_gb', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('games', 'storage_gb')
    op.add_column('games', sa.Column('storage_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_games_storage', 'games', 'storages', ['storage_id'], ['id'])