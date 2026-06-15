import json
import urllib.request

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyNjVjMDc5QGV4YW1wbGUuY29tIiwiZXhwIjoxNzgxMTU1MDMxfQ.y0Ff9DUH2sfCXLf3GqCztmAxpxkbszPu28a6ZokqXWo"

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/chat/sessions',
    data=json.dumps({'title': 'Test Chat'}).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    },
)
with urllib.request.urlopen(req) as resp:
    print('created', resp.status)
    print(resp.read().decode())
