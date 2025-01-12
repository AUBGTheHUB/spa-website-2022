from unittest.mock import Mock

import pytest
from result import Ok, Err

from src.database.model.participant_model import Participant
from src.database.model.team_model import Team
from src.server.exception import (
    DuplicateTeamNameError,
    DuplicateEmailError,
    ParticipantNotFoundError,
    TeamNotFoundError,
)
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.service.hackathon_service import HackathonService


@pytest.fixture
def hackathon_service(participant_repo_mock: Mock, team_repo_mock: Mock, tx_manager_mock: Mock) -> HackathonService:
    return HackathonService(participant_repo_mock, team_repo_mock, tx_manager_mock)


@pytest.mark.asyncio
async def test_create_participant_and_team_in_transaction(
    hackathon_service: HackathonService,
    mock_input_data: ParticipantRequestBody,
    participant_repo_mock: Mock,
    team_repo_mock: Mock,
    tx_manager_mock: Mock,
) -> None:
    # Mock successful `create` responses for team and participant. These are the operations inside the passed callback
    # to with_transaction
    team_repo_mock.create.return_value = Team(name=(mock_input_data.team_name if mock_input_data.team_name else ""))
    participant_repo_mock.create.return_value = Participant(
        name=mock_input_data.name,
        email=mock_input_data.email,
        is_admin=True,
        team_id=team_repo_mock.create.return_value.id,
    )

    # This is the result of the callback passed to with_transaction
    tx_manager_mock.with_transaction.return_value = Ok(
        (participant_repo_mock.create.return_value, team_repo_mock.create.return_value)
    )

    result = await hackathon_service.create_participant_and_team_in_transaction(mock_input_data)

    # Check that the result is an `Ok` containing both the participant and team objects
    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, tuple)
    assert isinstance(result.ok_value[0], Participant)
    assert isinstance(result.ok_value[1], Team)


@pytest.mark.asyncio
async def test_create_participant_and_team_in_transaction_duplicate_team_name_err(
    hackathon_service: HackathonService, mock_input_data: ParticipantRequestBody, tx_manager_mock: Mock
) -> None:
    # Mock an `Err` for duplicate team name returned from the passed callback to with_transaction. with_transaction
    # returns what the passed callback returns.
    tx_manager_mock.with_transaction.return_value = Err(DuplicateTeamNameError(mock_input_data.team_name))

    result = await hackathon_service.create_participant_and_team_in_transaction(mock_input_data)

    # Check that the result is an `Err` with `DuplicateTeamNameError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateTeamNameError)
    assert str(result.err_value) == mock_input_data.team_name


@pytest.mark.asyncio
async def test_create_participant_and_team_in_transaction_duplicate_email_err(
    hackathon_service: HackathonService, mock_input_data: ParticipantRequestBody, tx_manager_mock: Mock
) -> None:
    # Mock an `Err` for duplicate email returned from the passed callback to with_transaction. with_transaction
    # returns what the passed callback returns.
    tx_manager_mock.with_transaction.return_value = Err(DuplicateEmailError(mock_input_data.email))

    result = await hackathon_service.create_participant_and_team_in_transaction(mock_input_data)

    # Check that the result is an `Err` with `DuplicateEmailError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    assert str(result.err_value) == mock_input_data.email


@pytest.mark.asyncio
async def test_register_admin_participant_general_exception(
    hackathon_service: HackathonService, mock_input_data: ParticipantRequestBody, tx_manager_mock: Mock
) -> None:
    # Mock `with_transaction` to raise a general exception
    tx_manager_mock.with_transaction.return_value = Err(Exception("Test error"))

    result = await hackathon_service.create_participant_and_team_in_transaction(mock_input_data)

    # Verify the result is an `Err` containing a general Exception
    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    assert str(result.err_value) == "Test error"


@pytest.mark.asyncio
async def test_check_capacity_admin_case_with_sufficient_capacity(
    hackathon_service: HackathonService, participant_repo_mock: Mock, team_repo_mock: Mock
) -> None:
    # Mock repository methods to return controlled values
    participant_repo_mock.get_verified_random_participants_count.return_value = 18
    team_repo_mock.get_verified_registered_teams_count.return_value = 4

    # Mock MAX_NUMBER_OF_TEAM_MEMBERS and MAX_NUMBER_OF_TEAMS_IN_HACKATHON
    team_repo_mock.MAX_NUMBER_OF_TEAM_MEMBERS = 6
    team_repo_mock.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON = 12

    # Call the admin case capacity check function
    result = await hackathon_service.check_capacity_register_admin_participant_case()

    # Assert the result is True (enough capacity)
    assert result is True


@pytest.mark.asyncio
async def test_check_capacity_admin_case_with_exact_limit(
    hackathon_service: HackathonService, participant_repo_mock: Mock, team_repo_mock: Mock
) -> None:
    # Mock repository methods to return controlled values
    participant_repo_mock.get_verified_random_participants_count.return_value = 10
    team_repo_mock.get_verified_registered_teams_count.return_value = 10

    # Mock MAX_NUMBER_OF_TEAM_MEMBERS and MAX_NUMBER_OF_TEAMS_IN_HACKATHON
    team_repo_mock.MAX_NUMBER_OF_TEAM_MEMBERS = 6
    team_repo_mock.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON = 12

    # Call the admin case capacity check function
    result = await hackathon_service.check_capacity_register_admin_participant_case()

    # Assert the result is False (capacity exactly reached)
    assert result is False


@pytest.mark.asyncio
async def test_check_capacity_admin_case_with_exceeded_capacity(
    hackathon_service: HackathonService, participant_repo_mock: Mock, team_repo_mock: Mock
) -> None:
    # Mock repository methods to return controlled values
    participant_repo_mock.get_verified_random_participants_count.return_value = 15
    team_repo_mock.get_verified_registered_teams_count.return_value = 11

    # Mock MAX_NUMBER_OF_TEAM_MEMBERS and MAX_NUMBER_OF_TEAMS_IN_HACKATHON
    team_repo_mock.MAX_NUMBER_OF_TEAM_MEMBERS = 6
    team_repo_mock.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON = 12

    # Call the admin case capacity check function
    result = await hackathon_service.check_capacity_register_admin_participant_case()

    # Assert the result is False (capacity exceeded)
    assert result is False


@pytest.mark.asyncio
async def test_create_random_participant(
    hackathon_service: HackathonService,
    mock_input_data_random: ParticipantRequestBody,
    participant_repo_mock: Mock,
) -> None:
    # Mock successful `create` response for random participant.
    participant_repo_mock.create.return_value = Participant(
        name=mock_input_data_random.name,
        email=mock_input_data_random.email,
        is_admin=False,
        team_id=None,
    )

    # Return the `Ok` result from the mocked `create` method
    participant_repo_mock.create.return_value = Ok(participant_repo_mock.create.return_value)

    result = await hackathon_service.create_random_participant(mock_input_data_random)

    # Validate that the result is an `Ok` instance containing the participant object
    assert isinstance(result, Ok)
    assert isinstance(result.ok_value[0], Participant)  # Check the first element is a Participant
    assert result.ok_value[0].name == mock_input_data_random.name
    assert result.ok_value[0].email == mock_input_data_random.email
    assert not result.ok_value[0].is_admin  # Ensure it is not an admin
    assert result.ok_value[1] is None  # Ensure the second element is None


@pytest.mark.asyncio
async def test_create_random_participant_duplicate_email_err(
    hackathon_service: HackathonService, mock_input_data_random: ParticipantRequestBody, participant_repo_mock: Mock
) -> None:
    # Mock the `create` method to simulate a duplicate email error
    duplicate_email_error = DuplicateEmailError(mock_input_data_random.email)
    participant_repo_mock.create.return_value = Err(duplicate_email_error)

    result = await hackathon_service.create_random_participant(mock_input_data_random)

    # Check that the result is an `Err` with `DuplicateEmailError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    assert str(result.err_value) == mock_input_data_random.email


@pytest.mark.asyncio
async def test_register_random_participant_general_exception(
    hackathon_service: HackathonService, mock_input_data_random: ParticipantRequestBody, participant_repo_mock: Mock
) -> None:
    # Mock the `create` method to raise a general exception
    participant_repo_mock.create.return_value = Err(Exception("Test error"))

    result = await hackathon_service.create_random_participant(mock_input_data_random)

    # Verify the result is an `Err` containing a general Exception
    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    assert str(result.err_value) == "Test error"


@pytest.mark.asyncio
async def test_check_capacity_random_case_with_sufficient_capacity(
    hackathon_service: HackathonService, participant_repo_mock: Mock, team_repo_mock: Mock
) -> None:
    # Mock repository methods to return controlled values
    participant_repo_mock.get_verified_random_participants_count.return_value = 18
    team_repo_mock.get_verified_registered_teams_count.return_value = 4

    # Mock MAX_NUMBER_OF_TEAM_MEMBERS and MAX_NUMBER_OF_TEAMS_IN_HACKATHON
    team_repo_mock.MAX_NUMBER_OF_TEAM_MEMBERS = 6
    team_repo_mock.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON = 12

    # Call the random case capacity check function
    result = await hackathon_service.check_capacity_register_random_participant_case()

    # Assert the result is True (enough capacity)
    assert result is True


@pytest.mark.asyncio
async def test_check_capacity_random_case_with_exact_limit(
    hackathon_service: HackathonService, participant_repo_mock: Mock, team_repo_mock: Mock
) -> None:
    # Mock repository methods to return controlled values
    participant_repo_mock.get_verified_random_participants_count.return_value = 10
    team_repo_mock.get_verified_registered_teams_count.return_value = 10

    # Mock MAX_NUMBER_OF_TEAM_MEMBERS and MAX_NUMBER_OF_TEAMS_IN_HACKATHON
    team_repo_mock.MAX_NUMBER_OF_TEAM_MEMBERS = 6
    team_repo_mock.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON = 12

    # Call the random case capacity check function
    result = await hackathon_service.check_capacity_register_random_participant_case()

    # Assert the result is False (capacity exactly reached)
    assert result is True


@pytest.mark.asyncio
async def test_check_capacity_random_case_with_exceeded_capacity(
    hackathon_service: HackathonService, participant_repo_mock: Mock, team_repo_mock: Mock
) -> None:
    # Mock repository methods to return controlled values
    participant_repo_mock.get_verified_random_participants_count.return_value = 15
    team_repo_mock.get_verified_registered_teams_count.return_value = 11

    # Mock MAX_NUMBER_OF_TEAM_MEMBERS and MAX_NUMBER_OF_TEAMS_IN_HACKATHON
    team_repo_mock.MAX_NUMBER_OF_TEAM_MEMBERS = 6
    team_repo_mock.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON = 12

    # Call the admin case capacity check function
    result = await hackathon_service.check_capacity_register_random_participant_case()

    # Assert the result is False (capacity exceeded)
    assert result is False


@pytest.mark.asyncio
async def verify_admin_participant_and_team_in_transaction_success(
    hackathon_service: HackathonService,
    participant_repo_mock: Mock,
    team_repo_mock: Mock,
    tx_manager_mock: Mock,
    mock_input_data: JwtUserData,
) -> None:

    # Mocks update for team and participants repo
    team_repo_mock.update.return_value = Team(name="Test")
    participant_repo_mock.update.return_value = Participant(
        name="Test name",
        email="Test email",
        is_admin=True,
        team_id=team_repo_mock.update.return_value.id,
    )

    # Result the callback passed to with_transaction
    tx_manager_mock.with_transaction.return_value = Ok(
        (participant_repo_mock.create.return_value, team_repo_mock.create.return_value)
    )

    result = await hackathon_service.verify_admin_participant_and_team_in_transaction(mock_input_data)

    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, tuple)
    assert isinstance(result.ok_value[0], Participant)
    assert isinstance(result.ok_value[1], Team)


@pytest.mark.asyncio
async def verify_admin_participant_and_team_in_transaction_participant_not_found_error(
    hackathon_service: HackathonService, tx_manager_mock: Mock, mock_input_data: JwtUserData
) -> None:

    tx_manager_mock.with_transaction.return_value = Err(ParticipantNotFoundError())

    result = await hackathon_service.verify_admin_participant_and_team_in_transaction(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, ParticipantNotFoundError)


@pytest.mark.asyncio
async def verify_admin_participant_and_team_in_transaction_team_not_found_error(
    hackathon_service: HackathonService, tx_manager_mock: Mock, mock_input_data: JwtUserData
) -> None:

    tx_manager_mock.with_transaction.return_value = Err(TeamNotFoundError())

    result = await hackathon_service.verify_admin_participant_and_team_in_transaction(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, TeamNotFoundError)


@pytest.mark.asyncio
async def verify_admin_participant_and_team_in_transaction_general_error(
    hackathon_service: HackathonService, tx_manager_mock: Mock, mock_input_data: JwtUserData
) -> None:

    tx_manager_mock.with_transaction.return_value = Err(Exception("Test error"))

    result = await hackathon_service.verify_admin_participant_and_team_in_transaction(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    str(result.err_value) == "Test error"
