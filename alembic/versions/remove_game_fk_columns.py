"""remove foreign key columns from games

Revision ID: remove_game_fk_columns
Revises: add_storage_gb_column
Create Date: 2026-06-04 01:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "remove_game_fk_columns"
down_revision: Union[str, Sequence[str], None] = "add_storage_gb_column"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('fk_games_cpu', 'games', type_='foreignkey')
    op.drop_constraint('fk_games_gpu', 'games', type_='foreignkey')
    op.drop_constraint('fk_games_ram', 'games', type_='foreignkey')
    op.drop_column('games', 'cpu_id')
    op.drop_column('games', 'gpu_id')
    op.drop_column('games', 'ram_id')


def downgrade() -> None:
    op.add_column('games', sa.Column('cpu_id', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('gpu_id', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('ram_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_games_cpu', 'games', 'cpus', ['cpu_id'], ['id'])
    op.create_foreign_key('fk_games_gpu', 'games', 'gpus', ['gpu_id'], ['id'])
    op.create_foreign_key('fk_games_ram', 'games', 'rams', ['ram_id'], ['id'])