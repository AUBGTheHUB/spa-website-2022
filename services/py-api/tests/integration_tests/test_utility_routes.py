from unittest import mock
import pytest
from httpx import AsyncClient
from result import Err

PING_ENDPOINT_URL = "/api/v3/ping"


@pytest.mark.asyncio
async def test_ping_endpoint_service_unavailable(async_client: AsyncClient) -> None:
    with mock.patch("src.database.db_manager.DatabaseManager.async_ping_db", new_callable=mock.AsyncMock) as mock_ping:
        mock_ping.return_value = Err("Test err")
        resp = await async_client.get(PING_ENDPOINT_URL)
        assert resp.status_code == 503
        assert resp.json() == {"error": "Database not available!"}


@pytest.mark.asyncio
async def test_ping_endpoint(async_client: AsyncClient) -> None:
    resp = await async_client.get(PING_ENDPOINT_URL)
    assert resp.status_code == 200
    assert resp.json() == {"message": "pong"}
