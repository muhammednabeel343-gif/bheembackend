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
    with op.batch_alter_table('games', recreate='always') as batch_op:
        batch_op.add_column(sa.Column('cpu_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('gpu_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ram_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('storage_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.String(1000), nullable=True))
        batch_op.create_foreign_key('fk_games_cpu', 'cpus', ['cpu_id'], ['id'])
        batch_op.create_foreign_key('fk_games_gpu', 'gpus', ['gpu_id'], ['id'])
        batch_op.create_foreign_key('fk_games_ram', 'rams', ['ram_id'], ['id'])
        batch_op.create_foreign_key('fk_games_storage', 'storages', ['storage_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('games', recreate='always') as batch_op:
        batch_op.drop_constraint('fk_games_cpu', type_='foreignkey')
        batch_op.drop_constraint('fk_games_gpu', type_='foreignkey')
        batch_op.drop_constraint('fk_games_ram', type_='foreignkey')
        batch_op.drop_constraint('fk_games_storage', type_='foreignkey')
        batch_op.drop_column('cpu_id')
        batch_op.drop_column('gpu_id')
        batch_op.drop_column('ram_id')
        batch_op.drop_column('storage_id')
        batch_op.drop_column('description')