"""add hardware foreign keys to games table

Revision ID: 89012345abcd
Revises: 78901234abcd
Create Date: 2026-06-03 21:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "89012345abcd"
down_revision: Union[str, Sequence[str], None] = "78901234abcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('games', sa.Column('cpu_id', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('gpu_id', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('ram_id', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('storage_id', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('description', sa.String(1000), nullable=True))
    
    op.create_foreign_key('fk_games_cpu', 'games', 'cpus', ['cpu_id'], ['id'])
    op.create_foreign_key('fk_games_gpu', 'games', 'gpus', ['gpu_id'], ['id'])
    op.create_foreign_key('fk_games_ram', 'games', 'rams', ['ram_id'], ['id'])
    op.create_foreign_key('fk_games_storage', 'games', 'storages', ['storage_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_games_cpu', 'games', type_='foreignkey')
    op.drop_constraint('fk_games_gpu', 'games', type_='foreignkey')
    op.drop_constraint('fk_games_ram', 'games', type_='foreignkey')
    op.drop_constraint('fk_games_storage', 'games', type_='foreignkey')
    
    op.drop_column('games', 'cpu_id')
    op.drop_column('games', 'gpu_id')
    op.drop_column('games', 'ram_id')
    op.drop_column('games', 'storage_id')
    op.drop_column('games', 'description')