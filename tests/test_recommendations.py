import sys
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app


def run_test():
    client = TestClient(app)

    r = client.get('/api/recommendations')
    print('recommendations:', r.status_code, r.json())
    assert r.status_code == 200

    r2 = client.get('/api/recommendations/1')
    print('recommendations for game:', r2.status_code, r2.json())
    assert r2.status_code == 200

    r3 = client.get('/api/profile/1/insights')
    print('profile insights:', r3.status_code, r3.json())
    assert r3.status_code == 200


if __name__ == '__main__':
    run_test()
