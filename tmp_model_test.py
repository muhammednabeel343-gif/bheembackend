import sys
sys.path.append(r'd:/cv/gameproject 2/backend')
from app.services.google_ai_client import GoogleAIClient
from app.config import settings

print('ai_enabled', settings.ai_enabled)
print('api_key exists', bool(settings.ai_api_key))
models = ['models/gemini-2.5-flash']
for model in models:
    try:
        client = GoogleAIClient(api_key=settings.ai_api_key, enable=True)
        resp = client.generate_text('Hello world', max_tokens=16, model=model)
        print('MODEL', model, '=>', resp)
    except Exception as e:
        print('MODEL', model, 'ERROR', type(e).__name__, e)
