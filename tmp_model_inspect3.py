import os
import sys
sys.path.append(r'd:/cv/gameproject 2/backend')
from app.config import settings
import google.generativeai as ggen

os.environ['GOOGLE_API_KEY'] = settings.google_api_key or ''
print('API key env set:', bool(os.environ.get('GOOGLE_API_KEY')))
models = ['models/text-bison-001', 'models/gemini-2.5-flash', 'models/gemini-flash-latest', 'models/gemini-2.5-flash-image', 'models/gemini-2.5-pro']
for model in models:
    print('\n--- testing', model, '---')
    try:
        gen_model = ggen.GenerativeModel(model)
        chat = gen_model.start_chat()
        resp = chat.send_message('Hello world')
        print('response type', type(resp))
        print('has text', hasattr(resp, 'text'), resp.text if hasattr(resp, 'text') else None)
        print('has output_text', hasattr(resp, 'output_text'), getattr(resp, 'output_text', None))
        print('repr', repr(resp))
    except Exception as e:
        print('ERROR', type(e).__name__, e)
