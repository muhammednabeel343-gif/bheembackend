import os
import pytest
from subprocess import run, PIPE


def test_ai_integration_check():
    """Run the ai_integration_check script only when GOOGLE_API_KEY is set.

    This test is skipped in environments without the key so it is safe to include
    in the test suite and only exercised in CI when the secret is provided.
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        pytest.skip('GOOGLE_API_KEY not set; skipping live AI integration test')

    # Run the integration script and assert exit code 0
    p = run(['python', 'backend/scripts/ai_integration_check.py'], stdout=PIPE, stderr=PIPE, text=True, env=os.environ)
    stdout = p.stdout
    stderr = p.stderr
    assert p.returncode == 0, f'Integration check failed: exit={p.returncode}\nstdout={stdout}\nstderr={stderr}'
