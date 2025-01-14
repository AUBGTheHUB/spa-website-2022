from datetime import datetime
from typing import Tuple
from unittest.mock import Mock, AsyncMock

import pytest
from pymongo.errors import DuplicateKeyError
from result import Ok, Err

from src.database.db_manager import PARTICIPANTS_COLLECTION
from src.database.model.participant_model import Participant
from src.database.repository.participants_repository import ParticipantsRepository
from src.server.exception import DuplicateEmailError
from tests.integration_tests.conftest import TEST_USER_EMAIL


@pytest.fixture
def repo(db_manager_mock: Mock) -> ParticipantsRepository:
    return ParticipantsRepository(db_manager_mock, PARTICIPANTS_COLLECTION)


@pytest.mark.asyncio
async def test_create_participant_success(
    ten_sec_window: Tuple[datetime, datetime],
    mock_random_participant: Participant,
    repo: ParticipantsRepository,
) -> None:
    start_time, end_time = ten_sec_window

    result = await repo.create(mock_random_participant)

    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, Participant)
    assert result.ok_value.name == mock_random_participant.name
    assert result.ok_value.email == mock_random_participant.email
    assert result.ok_value.is_admin is mock_random_participant.is_admin
    assert result.ok_value.email_verified is mock_random_participant.email_verified
    assert result.ok_value.team_id is mock_random_participant.team_id
    assert start_time <= result.ok_value.created_at <= end_time, "created_at is not within the 10-second window"
    assert start_time <= result.ok_value.updated_at <= end_time, "updated_at is not within the 10-second window"


@pytest.mark.asyncio
async def test_create_participant_duplicate_email_error(
    db_manager_mock: Mock, mock_random_participant: Participant, repo: ParticipantsRepository
) -> None:
    # Simulate a DuplicateKeyError raised by insert_one to represent a duplicate email
    db_manager_mock.get_collection.return_value.insert_one = AsyncMock(
        side_effect=DuplicateKeyError("Duplicate email error")
    )

    result = await repo.create(mock_random_participant)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    # Check that the error message is the duplicate email as expected
    assert str(result.err_value) == TEST_USER_EMAIL


@pytest.mark.asyncio
async def test_create_participant_general_exception(
    db_manager_mock: Mock, mock_random_participant: Participant, repo: ParticipantsRepository
) -> None:
    # Simulate a general exception raised by insert_one
    db_manager_mock.get_collection.return_value.insert_one = AsyncMock(side_effect=Exception("Test error"))

    result = await repo.create(mock_random_participant)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    # Check that the error message is the one in the Exception
    assert str(result.err_value) == "Test error"
