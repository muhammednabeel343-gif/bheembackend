"""Run Alembic migrations programmatically.

Usage:
    python backend/scripts/run_migrations.py --db-url <DATABASE_URL> [--dry-run]

Notes:
- This script will refuse to run against SQLite in-memory.
- It prints commands and runs `alembic upgrade head` using Alembic API.
"""
import os
import sys
import argparse
from alembic import command
from alembic.config import Config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-url', required=False, help='Database URL (overrides env var DATABASE_URL)')
    parser.add_argument('--dry-run', action='store_true', help='Print planned actions and exit')
    args = parser.parse_args()

    db_url = args.db_url or os.environ.get('DATABASE_URL')
    if not db_url:
        print('DATABASE_URL not provided. Set env var or pass --db-url.')
        sys.exit(2)

    # Ensure Alembic env.py picks up the requested DATABASE_URL instead of
    # environment/default .env values. Set it in the process environment early.
    os.environ['DATABASE_URL'] = db_url

    if db_url.startswith('sqlite:///:memory:'):
        print('Refusing to run migrations against in-memory SQLite. Provide a file-based or real DB URL.')
        sys.exit(3)

    print('Using DATABASE_URL=', db_url)

    script_location = os.path.join(os.path.dirname(__file__), '..', 'alembic')
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)

    if args.dry_run:
        print('Dry run: would run alembic upgrade head')
        sys.exit(0)

    try:
        print('Running alembic upgrade heads...')
        # Use 'heads' to apply all head revisions when repository has multiple heads
        command.upgrade(alembic_cfg, 'heads')
        print('Migration complete.')
    except Exception as e:
        print('Migration failed:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
