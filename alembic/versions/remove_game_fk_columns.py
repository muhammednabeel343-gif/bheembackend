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
    with op.batch_alter_table('games', recreate='always') as batch_op:
        batch_op.drop_constraint('fk_games_cpu', type_='foreignkey')
        batch_op.drop_constraint('fk_games_gpu', type_='foreignkey')
        batch_op.drop_constraint('fk_games_ram', type_='foreignkey')
        batch_op.drop_column('cpu_id')
        batch_op.drop_column('gpu_id')
        batch_op.drop_column('ram_id')


def downgrade() -> None:
    with op.batch_alter_table('games', recreate='always') as batch_op:
        batch_op.add_column(sa.Column('cpu_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('gpu_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ram_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_games_cpu', 'cpus', ['cpu_id'], ['id'])
        batch_op.create_foreign_key('fk_games_gpu', 'gpus', ['gpu_id'], ['id'])
        batch_op.create_foreign_key('fk_games_ram', 'rams', ['ram_id'], ['id'])