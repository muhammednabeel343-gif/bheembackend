"""create_app_schema

Revision ID: 001_create_app_schema
Revises:
Create Date: 2026-06-03 10:47:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_create_app_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_username', 'users', ['username'], unique=False)

    op.create_table(
        'games',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('genre', sa.String(100)),
        sa.Column('publisher', sa.String(255)),
        sa.Column('release_date', sa.Date),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_games_name', 'games', ['name'], unique=False)
    op.create_index('idx_games_genre', 'games', ['genre'], unique=False)

    op.create_table(
        'requirements',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('game_id', sa.Integer, sa.ForeignKey('games.id'), nullable=False),
        sa.Column('cpu', sa.String(100)),
        sa.Column('gpu', sa.String(100)),
        sa.Column('ram', sa.Integer),
        sa.Column('storage', sa.Integer),
        sa.Column('directx', sa.String(20)),
        sa.Column('os', sa.String(50)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_requirements_game_id', 'requirements', ['game_id'], unique=False)

    op.create_table(
        'favorites',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('game_id', sa.Integer, sa.ForeignKey('games.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('user_id', 'game_id', name='unique_user_game'),
    )
    op.create_index('idx_favorites_user_id', 'favorites', ['user_id'], unique=False)
    op.create_index('idx_favorites_game_id', 'favorites', ['game_id'], unique=False)

    op.create_table(
        'user_scans',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('game_id', sa.Integer, sa.ForeignKey('games.id'), nullable=True),
        sa.Column('cpu', sa.String(255), nullable=False),
        sa.Column('gpu', sa.String(255), nullable=False),
        sa.Column('ram_gb', sa.Integer, nullable=False),
        sa.Column('storage_gb', sa.Integer, nullable=False),
        sa.Column('operating_system', sa.String(100), nullable=True),
        sa.Column('compatibility_score', sa.Float, nullable=False),
        sa.Column('fps_estimate', sa.Integer, nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('scan_time', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_user_scans_user_id', 'user_scans', ['user_id'], unique=False)
    op.create_index('idx_user_scans_game_id', 'user_scans', ['game_id'], unique=False)
    op.create_index('idx_user_scans_scan_time', 'user_scans', ['scan_time'], unique=False)


def downgrade() -> None:
    op.drop_table('user_scans')
    op.drop_table('favorites')
    op.drop_table('requirements')
    op.drop_table('games')
    op.drop_table('users')
