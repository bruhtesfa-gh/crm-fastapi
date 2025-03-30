from typing import Dict

from httpx import AsyncClient


async def test_get_users(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.get("/users/me", headers=admin_token_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "admin@gmail.com"


async def test_get_user_by_id(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.get("/users/1", headers=admin_token_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "admin@gmail.com"


async def test_get_user_by_id_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.get("/users/999", headers=admin_token_headers)
    assert r.status_code == 404


async def test_update_user(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.put(
        "/users/2", headers=admin_token_headers, json={"username": "testuser@gmail.com"}
    )
    assert r.status_code == 403


async def test_update_user_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> None:
    r = await client.put(
        "/users/999",
        headers=admin_token_headers,
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
