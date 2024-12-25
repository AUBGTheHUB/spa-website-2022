from datetime import datetime
from typing import Tuple
from unittest.mock import Mock, AsyncMock

import pytest
from pymongo.errors import DuplicateKeyError
from result import Ok, Err

from src.database.db_manager import TEAMS_COLLECTION
from src.database.repository.teams_repository import TeamsRepository
from src.server.exception import DuplicateTeamNameError
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.database.model.team_model import Team


@pytest.fixture
def repo(db_manager_mock: Mock) -> TeamsRepository:
    return TeamsRepository(db_manager_mock, TEAMS_COLLECTION)


@pytest.mark.asyncio
async def test_create_team_success(
    ten_sec_window: Tuple[datetime, datetime],
    mock_input_data: ParticipantRequestBody,
    repo: TeamsRepository,
) -> None:
    start_time, end_time = ten_sec_window

    result = await repo.create(mock_input_data)

    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, Team)
    assert result.ok_value.name == mock_input_data.team_name
    # Check that created_at and updated_at fall within the 10-second window
    assert start_time <= result.ok_value.created_at <= end_time, "created_at is not within the 10-second window"
    assert start_time <= result.ok_value.updated_at <= end_time, "updated_at is not within the 10-second window"


@pytest.mark.asyncio
async def test_create_team_duplicate_name_error(
    db_manager_mock: Mock, mock_input_data: ParticipantRequestBody, repo: TeamsRepository
) -> None:
    # Simulate a DuplicateKeyError raised by insert_one to represent a duplicate team name
    db_manager_mock.retry_db_operation = AsyncMock(side_effect=DuplicateKeyError("Duplicate team name error"))

    result = await repo.create(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateTeamNameError)
    # Check that the error message contains the team name
    assert str(result.err_value) == "Test Team"


@pytest.mark.asyncio
async def test_create_team_general_exception(
    db_manager_mock: Mock, mock_input_data: ParticipantRequestBody, repo: TeamsRepository
) -> None:
    # Simulate a general exception raised by insert_one
    db_manager_mock.retry_db_operation = AsyncMock(side_effect=Exception("Test error"))

    result = await repo.create(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    # Check that the error message is the one in the Exception
    assert str(result.err_value) == "Test error"
