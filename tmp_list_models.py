import os
import sys
sys.path.append(r'd:/cv/gameproject 2/backend')
from app.config import settings
import google.generativeai as ggen

os.environ['GOOGLE_API_KEY'] = settings.google_api_key or ''
print('api_key exists', bool(settings.ai_api_key))
print('GOOGLE_API_KEY env', bool(os.environ.get('GOOGLE_API_KEY')))
print('has list_models', hasattr(ggen, 'list_models'))
if hasattr(ggen, 'list_models'):
    models = ggen.list_models()
    print('models type', type(models))
    try:
        for m in models:
            print('model', getattr(m, 'name', m))
    except Exception as e:
        print('models iteration failed', type(e).__name__, e)
