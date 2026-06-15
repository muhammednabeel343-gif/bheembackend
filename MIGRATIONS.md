Running Migrations (staging/production)
=======================================

This guide explains how to safely run Alembic migrations for the backend.

Prerequisites
-------------
- Access to the target database (staging or production).
- `DATABASE_URL` environment variable pointing to the DB (Postgres recommended).
- `alembic` and the project's Python dependencies installed in the environment.

Safe steps
----------
1. Inspect pending migrations:

```bash
# from project root
python -c "from alembic.config import Config; c=Config('backend/alembic.ini'); print(c.get_section('alembic'))"
alembic -c backend/alembic.ini current
alembic -c backend/alembic.ini history --verbose
```

2. Run a dry-run (no-op) to confirm connectivity and configuration:

```bash
python backend/scripts/run_migrations.py --db-url "$DATABASE_URL" --dry-run
```

3. Backup DB (highly recommended) using your DB provider tools or `pg_dump` for Postgres.

4. Run migrations:

```bash
python backend/scripts/run_migrations.py --db-url "$DATABASE_URL"
```

5. Verify tables exist and app can connect. Example quick check (Postgres):

```bash
# inspect new tables
psql "$DATABASE_URL" -c "\dt"
```

6. Run the integration tests or hit the AI endpoints in staging to confirm behavior:

```bash
# set env vars in staging for AI features if desired
curl -X POST "$STAGING_URL/api/ai/compatibility-explanation" -H "Content-Type: application/json" -d '{"game_id": 1, "user_system": {...}}'
```

Troubleshooting
---------------
- If migrations fail due to missing extensions or permissions, consult your DB admin and do not proceed without a backup.
- If the app expects AI cache tables but migration hasn't run, the endpoints will error; run the migration before enabling AI features in production.

Automation
----------
- You can call the same script from CI/CD pipelines with environment variables.
- Ensure secrets are stored securely and migration runs are gated (manual approval) for production.

GitHub Actions example
----------------------
The repository includes a manual GitHub Actions workflow at `.github/workflows/migrations.yml`.

How it works:
- Trigger via "Actions" → "Run Migrations (manual)" or via workflow_dispatch API.
- The job uses a GitHub `environment` (defaults to `staging`) which can be protected with required reviewers.
- The workflow reads `DATABASE_URL` from repository/org secrets and executes `backend/scripts/run_migrations.py`.

Before triggering the workflow:
- Set `DATABASE_URL` as a repository secret or in the target environment's secrets.
- Protect the `production` or `staging` environment in GitHub settings if you want manual approvals.

Example (manual trigger):

1. Go to the repository Actions tab
2. Select "Run Migrations (manual)"
3. Choose `environment` (staging/production) and click "Run workflow"

