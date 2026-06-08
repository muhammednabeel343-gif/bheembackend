"""Create activities table

Revision ID: create_activities_table
Revises: remove_game_fk_columns
Create Date: 2026-06-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_activities_table'
down_revision = 'remove_game_fk_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('entity_name', sa.String(255), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_entity_type'), 'activities', ['entity_type'], unique=False)
    op.create_index(op.f('ix_activities_entity_id'), 'activities', ['entity_id'], unique=False)
    op.create_index(op.f('ix_activities_action'), 'activities', ['action'], unique=False)
    op.create_index(op.f('ix_activities_timestamp'), 'activities', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_activities_timestamp'), table_name='activities')
    op.drop_index(op.f('ix_activities_action'), table_name='activities')
    op.drop_index(op.f('ix_activities_entity_id'), table_name='activities')
    op.drop_index(op.f('ix_activities_entity_type'), table_name='activities')
    op.drop_table('activities')
