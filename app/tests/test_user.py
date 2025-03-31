from typing import Dict

import pytest
from httpx import AsyncClient

_admin_token_headers = {
    "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDU5NTk4NDQuMDI4NywibmJmIjoxNzQzMzY3ODQ0LCJzdWIiOiIxIiwidXNlciI6eyJjcmVhdGVkX2F0IjoiMjAyNS0wMy0zMFQxODo0OTo1NS43OTA1NzUiLCJ1cGRhdGVkX2F0IjoiMjAyNS0wMy0zMFQxODo0OTo1NS43OTA1NzUiLCJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbkBnbWFpbC5jb20iLCJyb2xlX2lkIjoxLCJyb2xlIjp7ImlkIjoxLCJuYW1lIjoiQWRtaW4iLCJkZXNjcmlwdGlvbiI6IkFkbWluIHdpdGggcGVybWlzc2lvbiB0byBtYW5hZ2UgdXNlcnMsIHJvbGVzLCBhbmQgYXVkaXQgbG9ncy4iLCJwZXJtaXNzaW9ucyI6W3siaWQiOjIsIm5hbWUiOiJHRVQ6L3VzZXJzL21lLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBHRVQ6L3VzZXJzL21lLyJ9LHsiaWQiOjMsIm5hbWUiOiJHRVQ6L3VzZXJzLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBHRVQ6L3VzZXJzLyJ9LHsiaWQiOjQsIm5hbWUiOiJHRVQ6L3VzZXJzLyovIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIEdFVDovdXNlcnMvKi8ifSx7ImlkIjo1LCJuYW1lIjoiUFVUOi91c2Vycy8qLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBQVVQ6L3VzZXJzLyovIn0seyJpZCI6NiwibmFtZSI6IkRFTEVURTovdXNlcnMvKi8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gREVMRVRFOi91c2Vycy8qLyJ9LHsiaWQiOjcsIm5hbWUiOiJQVVQ6L3VzZXJzLyovcm9sZS8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gUFVUOi91c2Vycy8qL3JvbGUvIn0seyJpZCI6OCwibmFtZSI6IkdFVDovcm9sZXMvIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIEdFVDovcm9sZXMvIn0seyJpZCI6OSwibmFtZSI6IlBPU1Q6L3JvbGVzLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBQT1NUOi9yb2xlcy8ifSx7ImlkIjoxMCwibmFtZSI6IkdFVDovcm9sZXMvKi8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gR0VUOi9yb2xlcy8qLyJ9LHsiaWQiOjExLCJuYW1lIjoiUFVUOi9yb2xlcy8qLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBQVVQ6L3JvbGVzLyovIn0seyJpZCI6MTIsIm5hbWUiOiJERUxFVEU6L3JvbGVzLyovIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIERFTEVURTovcm9sZXMvKi8ifSx7ImlkIjoxMywibmFtZSI6IlBPU1Q6L3JvbGVzLyovcGVybWlzc2lvbnMvKi8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gUE9TVDovcm9sZXMvKi9wZXJtaXNzaW9ucy8qLyJ9LHsiaWQiOjE0LCJuYW1lIjoiREVMRVRFOi9yb2xlcy8qL3Blcm1pc3Npb25zLyovIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIERFTEVURTovcm9sZXMvKi9wZXJtaXNzaW9ucy8qLyJ9XX19LCJ0eXBlIjoiYXBpIiwiYWN0aW9uIjoiYWNjZXNzIn0.Un09M0Z2FBks7U6dSjpMCSH4JmfXosiMDL9slzfKER4"
}


@pytest.mark.asyncio
async def test_get_users(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.get("/users/me", headers=_admin_token_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "admin@gmail.com"


async def test_get_user_by_id(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.get("/users/1", headers=_admin_token_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "admin@gmail.com"


async def test_get_user_by_id_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.get("/users/999", headers=_admin_token_headers)
    assert r.status_code == 404


async def test_update_user(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.put(
        "/users/2",
        headers=_admin_token_headers,
        json={"username": "testuser@gmail.com"},
    )
    assert r.status_code == 403


async def test_update_user_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.put(
        "/users/999",
        headers=_admin_token_headers,
        json={"username": "testuser@gmail.com"},
    )
    assert r.status_code == 404


async def test_delete_user(client: AsyncClient) -> None:
    new_user = await client.post(
        "/auth/register",
        json={
            "username": "testuser3@gmail.com",
            "password": "testpassword",
            "role": "Admin",
        },
    )
    assert new_user.status_code == 200
    # lohin
    login_data = {"username": "testuser3@gmail.com", "password": "testpassword"}
    login_response = await client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    user_token_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }
    assert login_response.status_code == 200
    new_user_id = new_user.json()["id"]
    # delete user
    r = await client.delete(f"/users/{new_user_id}", headers=user_token_headers)
    assert r.status_code == 200
