from unittest.mock import Mock

import pytest
from bson import ObjectId
from result import Ok, Err

from src.database.model.participant_model import Participant
from src.database.model.team_model import Team
from src.server.exception import DuplicateEmailError, DuplicateTeamNameError
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.service.participants_service import ParticipantService


@pytest.fixture
def participant_service(participant_repo_mock: Mock, team_repo_mock: Mock, tx_manager_mock: Mock) -> ParticipantService:
    return ParticipantService(participant_repo_mock, team_repo_mock, tx_manager_mock)


@pytest.mark.asyncio
async def test_create_participant_and_team_in_transaction_success(
    participant_service: ParticipantService,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock successful `create` responses for team and participant
    team_repo_mock.create.return_value = Ok(Team(name=mock_input_data.team_name))
    participant_repo_mock.create.return_value = Ok(
        Participant(
            name=mock_input_data.name,
            email=mock_input_data.email,
            is_admin=False,
            team_id=team_repo_mock.create.return_value.ok_value.id,
        )
    )

    # Call the function under test
    result = await participant_service._create_participant_and_team_in_transaction(mock_input_data)

    # Assert `create` calls were awaited once for each repository with expected arguments
    team_repo_mock.create.assert_awaited_once_with(mock_input_data, None)
    participant_repo_mock.create.assert_awaited_once_with(
        mock_input_data, None, team_id=team_repo_mock.create.return_value.ok_value.id
    )

    # Check that the result is an `Ok` containing both the participant and team objects
    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, tuple)
    assert isinstance(result.ok_value[0], Participant)
    assert isinstance(result.ok_value[1], Team)


@pytest.mark.asyncio
async def test_create_participant_and_team_in_transaction_team_duplicate_name_error(
    participant_service: ParticipantService,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock `team_repo.create` to return an `Err` for duplicate team name
    team_repo_mock.create.return_value = Err(DuplicateTeamNameError(mock_input_data.team_name))

    # Call the function under test
    result = await participant_service._create_participant_and_team_in_transaction(mock_input_data)

    # Assert only the team `create` method was called, as the participant creation should be skipped
    team_repo_mock.create.assert_awaited_once_with(mock_input_data, None)
    participant_repo_mock.create.assert_not_awaited()

    # Check that the result is an `Err` with `DuplicateTeamNameError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateTeamNameError)
    assert str(result.err_value) == mock_input_data.team_name


@pytest.mark.asyncio
async def test_create_participant_and_team_in_transaction_participant_duplicate_email_error(
    participant_service: ParticipantService,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock successful team creation and simulate a duplicate email error in participant creation
    team_repo_mock.create.return_value = Ok(Team(name=mock_input_data.team_name))
    participant_repo_mock.create.return_value = Err(DuplicateEmailError(mock_input_data.email))

    # Call the function under test
    result = await participant_service._create_participant_and_team_in_transaction(mock_input_data)

    # Assert both `create` calls were awaited with the expected arguments
    team_repo_mock.create.assert_awaited_once_with(mock_input_data, None)
    participant_repo_mock.create.assert_awaited_once_with(
        mock_input_data, None, team_id=team_repo_mock.create.return_value.ok_value.id
    )

    # Check that the result is an `Err` with `DuplicateEmailError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    assert str(result.err_value) == mock_input_data.email


@pytest.mark.asyncio
async def test_register_admin_participant_success(
    participant_service: ParticipantService, tx_manager_mock: Mock, mock_input_data: ParticipantRequestBody
) -> None:
    # Mock transaction manager to call the `_create_participant_and_team_in_transaction` function
    tx_manager_mock.with_transaction.return_value = Ok(
        (
            Participant(name=mock_input_data.name, email=mock_input_data.email, is_admin=True, team_id=ObjectId()),
            Team(name=mock_input_data.team_name),
        )
    )

    # Call `register_admin_participant`
    result = await participant_service.register_admin_participant(mock_input_data)

    # Check that `with_transaction` was awaited once
    tx_manager_mock.with_transaction.assert_awaited_once_with(
        participant_service._create_participant_and_team_in_transaction, mock_input_data
    )

    # Verify the result is an `Ok` with a tuple containing participant and team
    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, tuple)
    assert isinstance(result.ok_value[0], Participant)
    assert isinstance(result.ok_value[1], Team)


@pytest.mark.asyncio
async def test_register_admin_participant_general_exception(
    participant_service: ParticipantService, tx_manager_mock: Mock, mock_input_data: ParticipantRequestBody
) -> None:
    # Mock `with_transaction` to raise a general exception
    tx_manager_mock.with_transaction.return_value = Err(Exception("Test error"))

    # Call `register_admin_participant`
    result = await participant_service.register_admin_participant(mock_input_data)

    # Check that `with_transaction` was awaited once
    tx_manager_mock.with_transaction.assert_awaited_once_with(
        participant_service._create_participant_and_team_in_transaction, mock_input_data
    )

    # Verify the result is an `Err` containing a general Exception
    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    assert str(result.err_value) == "Test error"
