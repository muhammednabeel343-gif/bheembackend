AI Integration (Google Generative AI)
====================================

This document explains how to safely enable and test real Google Generative AI integration for Phase 4.

Prerequisites
-------------
- A Google Cloud project with the Generative Language API enabled.
- A Web API key with appropriate quotas: `GOOGLE_API_KEY`.
- Optional: `GOOGLE_PROJECT_ID` (not required in all client versions).

Local setup
-----------
1. Install the optional client:

```bash
pip install google-generativeai==0.4.1
```

2. Add the following to `backend/.env` (do NOT commit this file):

```
GOOGLE_API_KEY=your_real_api_key_here
GOOGLE_PROJECT_ID=your_project_id_here  # optional
ENABLE_AI_FEATURES=true
```

3. Run the integration check script (safe: it will skip if key not present):

```bash
python backend/scripts/ai_integration_check.py
```

CI integration
--------------
- The repository CI includes an `ai-integration` job that runs only when the repository secret `GOOGLE_API_KEY` is set in GitHub Actions.
- This job installs the `google-generativeai` client and runs `backend/scripts/ai_integration_check.py`.

Security
--------
- Never commit API keys. Use GitHub repository secrets for CI and a secret manager (or environment) for staging/production.
- Monitor usage and quota to avoid unexpected charges.

Notes
-----
- The `GoogleAIClient` in `backend/app/services/google_ai_client.py` is implemented to fall back to mock mode if the library or API key is missing. This ensures current functionality remains safe and unchanged until you opt-in.

- Fail-fast startup: you can set `AI_FAIL_FAST_ON_INVALID=true` to have the app refuse to start when AI validation fails (useful for strict environments). By default this is `false` so the app will start and record the validation status at `GET /api/ai/status`.

Cost controls
-------------
- Sample rate: set `AI_REQUEST_SAMPLE_RATE` to a value between `0.0` and `1.0` to only send a fraction of requests to the real model (e.g. `0.1` for 10%). Default is `1.0` (all requests).
- Rate limit: set `AI_MAX_CALLS_PER_MINUTE` to an integer >0 to cap outgoing calls per minute. When the cap is exceeded, requests will fail fast and be retried by service code.

These settings are read at client instantiation and help avoid unexpected costs during early rollouts.
