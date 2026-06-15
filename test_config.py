from app.config import settings


def test_config():
    print("Testing configuration...")
    print(f"✅ Google API Key: {'Set' if settings.google_api_key else 'NOT SET'}")
    print(f"✅ AI Features Enabled: {settings.enable_ai_features}")
    print(f"✅ Temperature: {settings.ai_temperature_explanation}")
    print(f"✅ Max Tokens: {settings.ai_max_tokens}")


if __name__ == "__main__":
    test_config()
