import sys
sys.path.append(r'd:/cv/gameproject 2/backend')
from app.services.google_ai_client import GoogleAIClient
from app.config import settings

client = GoogleAIClient(api_key=settings.ai_api_key, enable=True)
resp = client._ggen.GenerativeModel('models/gemini-1.5-flash').start_chat().send_message('Hello world')
print('TYPE', type(resp))
print('DIR', [a for a in dir(resp) if not a.startswith('_')])
for attr in ['text', 'output_text', 'response', 'message', 'content', 'candidates', 'conversation', 'last']:
    try:
        print(attr, getattr(resp, attr))
    except Exception as e:
        print(attr, 'ERROR', e)
print('repr', repr(resp))
print('str', str(resp))
