from app.config import settings
from app.services.google_ai_client import GoogleAIClient
import sys


def run_check():
    if not settings.enable_ai_features:
        print("AI features not enabled (ENABLE_AI_FEATURES is false). Skipping integration check.")
        return 0

    if not settings.google_api_key:
        print("GOOGLE_API_KEY not set. To run a live integration check, set the key in backend/.env or environment.")
        return 2

    client = GoogleAIClient(api_key=settings.google_api_key, project_id=settings.google_project_id, enable=True)

    try:
        resp = client.generate_text("Say hello from GameReady integration test.")
        print("AI integration response:", resp)
        if not resp:
            print("AI integration returned empty response. Marking as failure.")
            return 3
        return 0
    except Exception as e:
        print("AI integration failed:", str(e))
        return 1


if __name__ == '__main__':
    code = run_check()
    sys.exit(code)
