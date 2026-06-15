import sys
sys.path.insert(0, 'backend')

from app.services.google_ai_client import GoogleAIClient
from app.services.ai_metrics import metrics

# Use a short retry count to keep the test quick
client = GoogleAIClient(enable=True, mock=False, max_retries=1)
# Force a fake library object so we exercise the real-call path without needing
# the external `google.generativeai` package. This simulates a successful
# call and updates metrics accordingly.
client.mock = False
class _FakeResp:
    def __init__(self, text):
        self.output_text = text

class _FakeGGen:
    @staticmethod
    def generate(*args, **kwargs):
        return _FakeResp('fake-model-output')

client._ggen = _FakeGGen()
try:
    client.generate_text('healthcheck-test', max_tokens=16)
except Exception as e:
    print('client error:', e)

print('metrics:', metrics.snapshot())
