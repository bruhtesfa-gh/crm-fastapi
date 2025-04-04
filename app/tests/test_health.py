import logging

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/")
    logging.info(r.json())
    assert r.status_code == 200
    assert r.json() == {
        "status": "ok",
        "message": "Hello from Async CRM Backend!",
    }
