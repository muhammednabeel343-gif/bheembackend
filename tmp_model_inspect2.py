import os
import sys
sys.path.append(r'd:/cv/gameproject 2/backend')
from app.config import settings
import google.generativeai as ggen

os.environ['GOOGLE_API_KEY'] = settings.google_api_key or ''
print('API key env set:', bool(os.environ.get('GOOGLE_API_KEY')))
print('has list_models', hasattr(ggen, 'list_models'))
print('supported attributes on ggen:', [a for a in dir(ggen) if a in ('configure','GenerativeModel','list_models','generate','responses')])
model = 'models/gemini-pro-latest'
print('testing model', model)
try:
    gen_model = ggen.GenerativeModel(model)
    print('model object', gen_model)
    chat = gen_model.start_chat()
    print('chat obj attrs', [a for a in dir(chat) if not a.startswith('_')])
    resp = chat.send_message('Hello world')
    print('response type', type(resp))
    print('response dir', [a for a in dir(resp) if not a.startswith('_')])
    for attr in ['text','output_text','message','response','content','candidates','last']:
        try:
            print(attr, getattr(resp, attr))
        except Exception as e:
            print(attr, 'ERROR', e)
    print('repr', repr(resp))
except Exception as e:
    import traceback
    traceback.print_exc()
