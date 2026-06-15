import sys
sys.path.insert(0, 'backend')
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    r = client.get('/api/ai/status')
    print('status code=', r.status_code)
    try:
        print(r.json())
    except Exception:
        print('non-json response', r.text)
