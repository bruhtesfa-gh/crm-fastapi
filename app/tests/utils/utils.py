import random
import string
from datetime import date
from typing import Dict, Optional

from fastapi.testclient import TestClient
from pydantic import UUID4

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=12))


def random_number() -> int:
    return random.randint(1, 10)


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_admin_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": "admin@gmail.com",
        "password": "admin123",
    }
    r = client.post("/auth/login", data=login_data)
    tokens = r.json()

    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
