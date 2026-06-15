from app.services.google_ai_client import GoogleAIClient


def test_generate_text_mock():
    client = GoogleAIClient(enable=False, mock=True)
    resp = client.generate_text("Hello world")
    print("generate_text mock response:", resp)
    assert isinstance(resp, dict)
    assert "text" in resp
    assert resp["text"].startswith("[MOCK]")


def test_generate_structured_mock():
    client = GoogleAIClient(enable=False, mock=True)
    schema = {"summary": "str", "advice": "str"}
    resp = client.generate_structured_response("Give advice", schema)
    print("generate_structured mock response:", resp)
    assert isinstance(resp, dict)
    assert set(resp.keys()) == set(schema.keys())


if __name__ == "__main__":
    test_generate_text_mock()
    test_generate_structured_mock()
    print("AI client mock tests passed")
