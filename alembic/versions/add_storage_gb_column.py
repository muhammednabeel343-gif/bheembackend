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
    with op.batch_alter_table('games', recreate='always') as batch_op:
        batch_op.drop_constraint('fk_games_storage', type_='foreignkey')
        batch_op.drop_column('storage_id')
        batch_op.add_column(sa.Column('storage_gb', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('games', recreate='always') as batch_op:
        batch_op.drop_column('storage_gb')
        batch_op.add_column(sa.Column('storage_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_games_storage', 'storages', ['storage_id'], ['id'])