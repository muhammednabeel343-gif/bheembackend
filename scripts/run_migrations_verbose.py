"""Run Alembic migrations and print full traceback on error (verbose helper)."""
import os
import sys
from alembic import command
from alembic.config import Config
import traceback

if __name__ == '__main__':
    db_url = os.environ.get('DATABASE_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not db_url:
        print('DATABASE_URL not provided. Usage: DATABASE_URL=... python run_migrations_verbose.py <db_url>')
        sys.exit(2)
    os.environ['DATABASE_URL'] = db_url
    script_location = os.path.join(os.path.dirname(__file__), '..', 'alembic')
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)
    try:
        print('Running alembic upgrade heads (verbose)...')
        command.upgrade(alembic_cfg, 'heads')
        print('Migration complete (verbose).')
    except Exception:
        traceback.print_exc()
        sys.exit(1)
