from unittest.mock import patch, AsyncMock

import pytest
from pymongo.errors import ConnectionFailure, PyMongoError, OperationFailure
from result import Err, Ok

from src.database.db_manager import DatabaseManager
from src.utils import SingletonMeta


# https://docs.pytest.org/en/6.2.x/fixture.html#autouse-fixtures-fixtures-you-don-t-have-to-request
@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    # Clear singleton instances before each test as we get inconsistent test results
    # Accessing private members of class like this is highly discouraged and is only possible as this is Python.
    # We do it only because this is an exceptional case. Using Singletons in unit tests could be tricky :(
    SingletonMeta._instances.clear()


@pytest.fixture
def db_manager() -> DatabaseManager:
    with patch("src.database.db_manager.AsyncIOMotorClient") as mock_client:
        mock_client.return_value.admin.command = AsyncMock(return_value={"ok": 1})
        # https://stackoverflow.com/questions/42565304/is-it-possible-to-ping-mongodb-from-pymongo
        with patch("src.database.db_manager.environ", {"DATABASE_URL": "mongodb+srv://test_url"}):
            return DatabaseManager()


# Define a custom exception to simulate retryable write error
class RetryableWriteError(PyMongoError):
    def has_error_label(self, label: str) -> bool:
        return label == "RetryableWriteError"


@pytest.fixture
def db_manager_err_operation() -> DatabaseManager:
    with patch("src.database.db_manager.AsyncIOMotorClient") as mock_client:
        mock_client.return_value.admin.command = AsyncMock(side_effect=ConnectionFailure("Test err"))
        # https://stackoverflow.com/questions/42565304/is-it-possible-to-ping-mongodb-from-pymongo
        with patch("src.database.db_manager.environ", {"DATABASE_URL": "mongodb+srv://test_url"}):
            return DatabaseManager()


@pytest.fixture
def db_manager_none_client() -> DatabaseManager:
    with patch("src.database.db_manager.AsyncIOMotorClient") as mock_client:
        mock_client.return_value = None
        # https://stackoverflow.com/questions/42565304/is-it-possible-to-ping-mongodb-from-pymongo
        with patch("src.database.db_manager.environ", {"DATABASE_URL": "mongodb+srv://test_url"}):
            return DatabaseManager()


@pytest.mark.asyncio
async def test_async_ping_db_success(db_manager: DatabaseManager) -> None:
    result = await db_manager.async_ping_db()
    assert result is None


@pytest.mark.asyncio
async def test_async_ping_db_err(db_manager_err_operation: DatabaseManager) -> None:
    result = await db_manager_err_operation.async_ping_db()
    assert isinstance(result, Err)


@pytest.mark.asyncio
async def test_close_all_connections_success(db_manager: DatabaseManager) -> None:
    result = db_manager.close_all_connections()
    assert result is None


@pytest.mark.asyncio
async def test_close_all_connections_err(db_manager_none_client: DatabaseManager) -> None:
    result = db_manager_none_client.close_all_connections()
    isinstance(result, Err)


@pytest.mark.asyncio
async def test_retry_read_db_operation_success(db_manager: DatabaseManager) -> None:
    # Mock a successful db operation
    mock_db_operation = AsyncMock(return_value=Ok("Success"))
    result = await db_manager.retry_db_operation(mock_db_operation, is_read_operation=True)

    assert mock_db_operation.call_count == 1
    assert result == Ok("Success")


@pytest.mark.asyncio
async def test_retry_read_db_operation_retryable_error(db_manager: DatabaseManager) -> None:
    # Mock a successful db operation
    mock_db_operation = AsyncMock(side_effect=[OperationFailure("Test err", 7), Ok("Success")])

    # We patch the sleep function for faster testing
    with patch("src.database.db_manager.sleep", new=AsyncMock()):
        result = await db_manager.retry_db_operation(mock_db_operation, is_read_operation=True)

        # On the first call it failed and on the second call it succeeded
        assert mock_db_operation.call_count == 2
        assert result == Ok("Success")


@pytest.mark.asyncio
async def test_retry_read_db_operation_retryable_error_exhaust_retries(db_manager: DatabaseManager) -> None:
    # Simulate a retryable read err that keeps failing
    mock_db_operation = AsyncMock(side_effect=OperationFailure("Test err", 7))
    with pytest.raises(PyMongoError):
        await db_manager.retry_db_operation(mock_db_operation, is_read_operation=True)

    assert mock_db_operation.call_count == 2


@pytest.mark.asyncio
async def test_retry_write_db_operation_success(db_manager: DatabaseManager) -> None:
    # Mock a successful db operation
    mock_db_operation = AsyncMock(return_value=Ok("Success"))
    result = await db_manager.retry_db_operation(mock_db_operation, is_read_operation=False)

    assert mock_db_operation.call_count == 1
    assert result == Ok("Success")


@pytest.mark.asyncio
async def test_write_read_db_operation_retryable_error(db_manager: DatabaseManager) -> None:
    # Mock a successful db operation
    mock_db_operation = AsyncMock(side_effect=[RetryableWriteError(), Ok("Success")])

    # We patch the sleep function for faster testing
    with patch("src.database.db_manager.sleep", new=AsyncMock()):
        result = await db_manager.retry_db_operation(mock_db_operation, is_read_operation=False)

        # On the first call it failed and on the second call it succeeded
        assert mock_db_operation.call_count == 2
        assert result == Ok("Success")


@pytest.mark.asyncio
async def test_retry_write_db_operation_retryable_error_exhaust_retries(db_manager: DatabaseManager) -> None:
    # Simulate a retryable read err that keeps failing
    mock_db_operation = AsyncMock(side_effect=RetryableWriteError())
    with pytest.raises(PyMongoError):
        await db_manager.retry_db_operation(mock_db_operation, is_read_operation=False)

    assert mock_db_operation.call_count == 2
