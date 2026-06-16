import httpx
import asyncio

N8N_WEBHOOK_URL = "https://nabx-777xx.app.n8n.cloud/webhook-test/38c6df7a-ba14-4bc1-8d54-27d3c085fffd"

test_payload = {
    "email": "test@example.com",
    "username": "TestUser",
    "order_id": 999,
    "total_amount": 199.99,
    "games": [
        {"id": 1, "name": "Cyberpunk 2077", "image_url": "https://via.placeholder.com/60x90", "price": 59.99},
        {"id": 2, "name": "Elden Ring", "image_url": "https://via.placeholder.com/60x90", "price": 59.99}
    ],
    "purchase_date": "2026-06-16T12:13:00+05:30"
}

async def test_webhook():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(N8N_WEBHOOK_URL, json=test_payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_webhook())