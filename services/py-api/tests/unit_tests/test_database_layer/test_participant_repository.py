from datetime import datetime
from typing import Tuple
from unittest.mock import Mock, AsyncMock

import pytest
from pymongo.errors import DuplicateKeyError
from result import Ok, Err

from src.database.db_manager import PARTICIPANTS_COLLECTION
from src.database.model.participant_model import Participant
from src.database.repository.participants_repository import ParticipantsRepository
from src.server.exception import DuplicateEmailError, ParticipantNotFoundError
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody


@pytest.fixture
def repo(db_manager_mock: Mock) -> ParticipantsRepository:
    return ParticipantsRepository(db_manager_mock, PARTICIPANTS_COLLECTION)


@pytest.mark.asyncio
async def test_create_participant_success(
    ten_sec_window: Tuple[datetime, datetime],
    mock_input_data: ParticipantRequestBody,
    repo: ParticipantsRepository,
) -> None:
    start_time, end_time = ten_sec_window

    result = await repo.create(mock_input_data)

    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, Participant)
    assert result.ok_value.name == mock_input_data.name
    assert result.ok_value.email == mock_input_data.email
    assert result.ok_value.is_admin == mock_input_data.is_admin
    assert result.ok_value.email_verified is False
    assert result.ok_value.team_id is None
    assert start_time <= result.ok_value.created_at <= end_time, "created_at is not within the 10-second window"
    assert start_time <= result.ok_value.updated_at <= end_time, "updated_at is not within the 10-second window"


@pytest.mark.asyncio
async def test_create_participant_duplicate_email_error(
    db_manager_mock: Mock, mock_input_data: ParticipantRequestBody, repo: ParticipantsRepository
) -> None:
    # Simulate a DuplicateKeyError raised by insert_one to represent a duplicate email
    db_manager_mock.get_collection.return_value.insert_one = AsyncMock(
        side_effect=DuplicateKeyError("Duplicate email error")
    )

    result = await repo.create(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    # Check that the error message is the duplicate email as expected
    assert str(result.err_value) == "test@example.com"


@pytest.mark.asyncio
async def test_create_participant_general_exception(
    db_manager_mock: Mock, mock_input_data: ParticipantRequestBody, repo: ParticipantsRepository
) -> None:
    # Simulate a general exception raised by insert_one
    db_manager_mock.get_collection.return_value.insert_one = AsyncMock(side_effect=Exception("Test error"))

    result = await repo.create(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    # Check that the error message is the one in the Exception
    assert str(result.err_value) == "Test error"


@pytest.mark.asyncio
async def test_delete_participant_success(
    db_manager_mock: Mock, mock_obj_id: str, repo: ParticipantsRepository
) -> None:

    db_manager_mock.get_collection.return_value.find_one_and_delete = AsyncMock(
        return_value={
            "name": "testtest",
            "email": "testtest@test.com",
            "email_verified": False,
            "is_admin": False,
            "team_id": None,
        }
    )

    result = await repo.delete(mock_obj_id)

    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, Participant)
    assert result.ok_value.id == mock_obj_id
    assert result.ok_value.name == "testtest"
    assert result.ok_value.email == "testtest@test.com"
    assert result.ok_value.email_verified is False
    assert result.ok_value.is_admin is False
    assert result.ok_value.team_id is None


@pytest.mark.asyncio
async def test_delete_participant_not_found(
    db_manager_mock: Mock, mock_obj_id: str, repo: ParticipantsRepository
) -> None:

    # When the participant with the sepcified object id is not found find_one_and_delete returns None
    db_manager_mock.get_collection.return_value.find_one_and_delete = AsyncMock(return_value=None)

    result = await repo.delete(mock_obj_id)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, ParticipantNotFoundError)


@pytest.mark.asyncio
async def test_delete_participant_general_exception(
    db_manager_mock: Mock, mock_obj_id: str, repo: ParticipantsRepository
) -> None:
    # Simulate a general exception raised by insert_one
    db_manager_mock.get_collection.return_value.find_one_and_delete = AsyncMock(side_effect=Exception("Test error"))

    result = await repo.delete(mock_obj_id)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    # Check that the error message is the one in the Exception
    assert str(result.err_value) == "Test error"


@pytest.mark.asyncio
async def test_update_participant_success(
    db_manager_mock: Mock, mock_obj_id: str, repo: ParticipantsRepository
) -> None:
    db_manager_mock.get_collection.return_value.find_one_and_update = AsyncMock(
        return_value={
            "name": "testtest",
            "email": "testtest@test.com",
            "email_verified": True,
            "is_admin": True,
            "team_id": None,
        }
    )

    result = await repo.update(mock_obj_id, {"email_verified": True, "name": "testtest"})

    assert isinstance(result, Ok)
    assert result.ok_value.id == mock_obj_id
    assert result.ok_value.email_verified is True
    assert result.ok_value.name == "testtest"
    assert result.ok_value.email == "testtest@test.com"
    assert result.ok_value.is_admin is True
    assert result.ok_value.team_id is None


@pytest.mark.asyncio
async def test_update_participant_not_found(
    db_manager_mock: Mock, mock_obj_id: str, repo: ParticipantsRepository
) -> None:
    # When a participant with the specified id is not found find_one_and_update returns None
    db_manager_mock.get_collection.return_value.find_one_and_update = AsyncMock(return_value=None)

    result = await repo.update(mock_obj_id, {"email_verified": True})

    assert isinstance(result, Err)
    assert isinstance(result.err_value, ParticipantNotFoundError)
