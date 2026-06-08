"""Create operating systems table

Revision ID: create_os_table
Revises: create_activities_table
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'create_os_table'
down_revision = 'create_activities_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'operating_systems',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_operating_systems_id'), 'operating_systems', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_operating_systems_id'), table_name='operating_systems')
    op.drop_table('operating_systems')
