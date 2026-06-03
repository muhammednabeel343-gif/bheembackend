# Project Bheem Backend

## Phase 1 Status

This backend implements the Phase 1 authentication foundation:

- FastAPI application (`app/main.py`)
- SQLAlchemy user model with email, username, hashed password, avatar URL, and timestamps
- JWT authentication with `/auth/register`, `/auth/login`, `/auth/logout`, and `/auth/me`
- `last_login_at` updated on successful login
- Environment configuration via `.env` / `.env.example`
- Optional MySQL support using `PyMySQL`

## Run locally

1. Activate the virtual environment:
   - Windows PowerShell:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```

2. Install dependencies:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update any values as needed.

4. Start the app:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app --port 8000
   ```

5. Open API docs in a browser:
   - `http://127.0.0.1:8000/docs`

6. When running the frontend locally, the backend CORS configuration supports:
   - `http://localhost:3000`
   - `http://localhost:5173`

## Notes

- The backend currently defaults to SQLite but supports MySQL when `DATABASE_URL` is set to a valid `mysql+pymysql://...` URI.
- The frontend for Phase 1 is not yet initialized in this workspace.
