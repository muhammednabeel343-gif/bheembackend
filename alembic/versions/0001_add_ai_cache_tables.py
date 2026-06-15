"""add ai cache tables

Revision ID: 0001_add_ai_cache_tables
Revises: 
Create Date: 2026-06-09 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_ai_cache_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'explanation_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cache_key', sa.String(length=128), nullable=False, unique=True),
        sa.Column('request', sa.JSON(), nullable=False),
        sa.Column('response', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'upgrade_recommendations_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cache_key', sa.String(length=128), nullable=False, unique=True),
        sa.Column('request', sa.JSON(), nullable=False),
        sa.Column('response', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    op.drop_table('upgrade_recommendations_cache')
    op.drop_table('explanation_cache')
