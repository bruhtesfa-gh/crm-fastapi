import json
from typing import Dict
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
import logging

async def admin_token(client: AsyncClient) -> str:
    login_data = {"username": "admin@gmail.com", "password": "admin123"}
    # Send form-encoded data to /auth/login
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert data["me"]["username"] == "admin@gmail.com"


async def test_register_user(client: AsyncClient) -> None:
    register_data = {
        "username": "testuser@gmail.com",
        "password": "testpassword",
        "role": "Admin"
    }
    headers = {"Content-Type": "application/json"}
    response = await client.post("/auth/register", json=jsonable_encoder(register_data), headers=headers)   
    assert response.status_code == 200, f"Register failed: {response.text}"
    data = response.json()
    assert data["username"] == "testuser@gmail.com"

