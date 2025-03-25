# test_main.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_lead():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/leads/", json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
