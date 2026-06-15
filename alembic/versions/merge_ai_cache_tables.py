"""merge ai cache tables branch with main app schema

Revision ID: merge_ai_cache_tables
Revises: 0001_add_ai_cache_tables, create_os_table
Create Date: 2026-06-09 00:30:00.000000
"""
from alembic import op
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'merge_ai_cache_tables'
down_revision: Union[str, Sequence[str], None] = ('0001_add_ai_cache_tables', 'create_os_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # merge revision: no direct schema changes
    pass


def downgrade() -> None:
    # cannot safely downgrade merged branches automatically
    raise NotImplementedError('Downgrade not supported for merge revision.')
