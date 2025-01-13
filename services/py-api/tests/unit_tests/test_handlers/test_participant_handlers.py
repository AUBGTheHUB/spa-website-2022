import pytest
from bson import ObjectId
from result import Err, Ok
from starlette import status

from src.database.model.participant_model import Participant
from src.database.model.team_model import Team
from src.server.exception import DuplicateTeamNameError, DuplicateEmailError, HackathonCapacityExceededError, TeamCapacityExceededError, TeamNotFoundError
from src.server.handlers.participants_handlers import ParticipantHandlers
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.server.schemas.response_schemas.schemas import ErrResponse, ParticipantRegisteredResponse
from unittest.mock import AsyncMock, Mock, MagicMock


@pytest.fixture
def participant_handlers(participant_registration_service_mock: Mock) -> ParticipantHandlers:
    return ParticipantHandlers(participant_registration_service_mock)


@pytest.mark.asyncio
async def test_create_participant_admin_case_success(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock successful result from `register_admin_participant`
    participant_registration_service_mock.register_admin_participant.return_value = Ok(
        (
            Participant(name="Test User", email="test@example.com", is_admin=True, team_id=ObjectId()),
            Team(name="Test Team"),
        )
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data)

    # Check that `register_admin_participant` was awaited once with the expected input_data
    participant_registration_service_mock.register_admin_participant.assert_awaited_once_with(mock_input_data)

    # Assert that the response is successful
    assert isinstance(result, ParticipantRegisteredResponse)
    assert result.participant.name == "Test User"
    assert result.team.name == "Test Team"
    assert response_mock.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_participant_admin_case_duplicate_email_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_admin_participant` to return an `Err` with `DuplicateEmailError`
    participant_registration_service_mock.register_admin_participant.return_value = Err(
        DuplicateEmailError(mock_input_data.email)
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data)

    # Check that `register_admin_participant` was awaited once
    participant_registration_service_mock.register_admin_participant.assert_awaited_once_with(mock_input_data)

    # Assert the response indicates a conflict
    assert isinstance(result, ErrResponse)
    assert result.error == "Participant with this email already exists"
    assert response_mock.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_participant_admin_case_duplicate_team_name_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_admin_participant` to return an `Err` with `DuplicateTeamNameError`
    participant_registration_service_mock.register_admin_participant.return_value = Err(
        DuplicateTeamNameError(mock_input_data.team_name)
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data)

    # Check that `register_admin_participant` was awaited once
    participant_registration_service_mock.register_admin_participant.assert_awaited_once_with(mock_input_data)

    # Assert the response indicates a conflict
    assert isinstance(result, ErrResponse)
    assert result.error == "Team with this name already exists"
    assert response_mock.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_participant_admin_case_general_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_admin_participant` to return a general `Err`
    participant_registration_service_mock.register_admin_participant.return_value = Err(Exception("General error"))

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data)

    # Check that `register_admin_participant` was awaited once
    participant_registration_service_mock.register_admin_participant.assert_awaited_once_with(mock_input_data)

    # Assert the response indicates an internal server error
    assert isinstance(result, ErrResponse)
    assert result.error == "An unexpected error occurred during the creation of Participant"
    assert response_mock.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_participant_admin_case_capacity_exceeded_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_admin_participant` to return an `Err` with `CapacityExceededError`
    participant_registration_service_mock.register_admin_participant.return_value = Err(
        HackathonCapacityExceededError()
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data)

    # Check that `register_admin_participant` was awaited once
    participant_registration_service_mock.register_admin_participant.assert_awaited_once_with(mock_input_data)

    # Assert the response indicates a conflict with capacity reached
    assert isinstance(result, ErrResponse)
    assert result.error == "Max hackathon capacity has been reached"
    assert response_mock.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_participant_random_case_success(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: AsyncMock,
    mock_input_data_random: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:

    # Mock the result from `register_random_participant`
    participant_registration_service_mock.register_random_participant.return_value = Ok(
        (
            Participant(name="Test User", email="test@example.com", is_admin=False, team_id=None),
            None,
        )
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_random)

    # Check that `register_random_participant` was awaited once with the expected input_data
    participant_registration_service_mock.register_random_participant.assert_awaited_once_with(mock_input_data_random)

    # Assert that the response is successful
    assert isinstance(result, ParticipantRegisteredResponse)
    assert result.participant.name == "Test User"
    assert response_mock.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_participant_random_case_duplicate_email_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_random_participant` to return an `Err` with `DuplicateEmailError`
    participant_registration_service_mock.register_random_participant.return_value = Err(
        DuplicateEmailError(mock_input_data_random.email)
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_random)

    # Check that `register_random_participant` was awaited once
    participant_registration_service_mock.register_random_participant.assert_awaited_once_with(mock_input_data_random)

    # Assert the response indicates a conflict
    assert isinstance(result, ErrResponse)
    assert result.error == "Participant with this email already exists"
    assert response_mock.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_participant_random_case_general_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_random_participant` to return a general `Err`
    participant_registration_service_mock.register_random_participant.return_value = Err(Exception("General error"))

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_random)

    # Check that `register_random_participant` was awaited once
    participant_registration_service_mock.register_random_participant.assert_awaited_once_with(mock_input_data_random)

    # Assert the response indicates an internal server error
    assert isinstance(result, ErrResponse)
    assert result.error == "An unexpected error occurred during the creation of Participant"
    assert response_mock.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_participant_random_case_capacity_exceeded_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_random_participant` to return an `Err` with `CapacityExceededError`
    participant_registration_service_mock.register_random_participant.return_value = Err(
        HackathonCapacityExceededError()
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_random)

    # Check that `register_random_participant` was awaited once
    participant_registration_service_mock.register_random_participant.assert_awaited_once_with(mock_input_data_random)

    # Assert the response indicates a conflict with capacity reached
    assert isinstance(result, ErrResponse)
    assert result.error == "Max hackathon capacity has been reached"
    response_mock.status_code = status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_create_participant_link_case_success(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Set the mocked return value for register_invite_link_participant
    participant_registration_service_mock.register_invite_link_participant.return_value = Ok(
        (
            Participant(name="Test User", email="test@example.com", is_admin=False, team_id=ObjectId()),
            None
        )
    )

    # Call the handler
    result = await participant_handlers.create_participant(
        response_mock, 
        mock_input_data_link, 
        jwt_token="example.token"
    )

    # Assertions
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(
        mock_input_data_link, 
        "example.token"
    )
    assert isinstance(result, ParticipantRegisteredResponse)
    assert result.participant.name == "Test User"
    response_mock.status_code = status.HTTP_200_OK

@pytest.mark.asyncio
async def test_create_participant_link_case_duplicate_email_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_invite_link_participant` to return an `Err` with `DuplicateEmailError`
    participant_registration_service_mock.register_invite_link_participant.return_value = Err(
        DuplicateEmailError(mock_input_data_link.email)
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_link, "example.token")

    # Check that `register_invite_link_participant` was awaited once
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(mock_input_data_link, "example.token")

    # Assert the response indicates a conflict
    assert isinstance(result, ErrResponse)
    assert result.error == "Participant with this email already exists"
    response_mock.status_code = status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_create_participant_link_case_duplicate_team_name_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_invite_link_participant` to return an `Err` with `DuplicateTeamNameError`
    participant_registration_service_mock.register_invite_link_participant.return_value = Err(
        DuplicateTeamNameError(mock_input_data_link.team_name)
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_link, "example.token")

    # Check that `register_invite_link_participant` was awaited once
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(mock_input_data_link, "example.token")

    # Assert the response indicates a conflict
    assert isinstance(result, ErrResponse)
    assert result.error == "Team with this name already exists"
    response_mock.status_code = status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_create_participant_invite_link_case_general_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_invite_link_participant` to return a general `Err`
    participant_registration_service_mock.register_invite_link_participant.return_value = Err(Exception("General error"))

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_link, "example.token")

    # Check that `register_admin_participant` was awaited once
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(mock_input_data_link, "example.token")

    # Assert the response indicates an internal server error
    assert isinstance(result, ErrResponse)
    assert result.error == "An unexpected error occurred during the creation of Participant"
    response_mock.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_create_participant_invite_link_case_hackathon_capacity_exceeded_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_invite_link_participant` to return an `Err` with `HackathonCapacityExceededError`
    participant_registration_service_mock.register_invite_link_participant.return_value = Err(
        HackathonCapacityExceededError()
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_link, "example.token")

    # Check that `register_invite_link_participant` was awaited once
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(mock_input_data_link, "example.token")

    # Assert the response indicates a conflict with capacity reached
    assert isinstance(result, ErrResponse)
    assert result.error == "Max hackathon capacity has been reached"
    response_mock.status_code = status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_create_participant_invite_link_case_team_capacity_exceeded_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_invite_link_participant` to return an `Err` with `TeamCapacityExceededError`
    participant_registration_service_mock.register_invite_link_participant.return_value = Err(
        TeamCapacityExceededError()
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_link, "example.token")

    # Check that `register_invite_link_participant` was awaited once
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(mock_input_data_link, "example.token")

    # Assert the response indicates a conflict with capacity reached
    assert isinstance(result, ErrResponse)
    assert result.error == "Max team capacity has been reached"
    response_mock.status_code = status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_create_participant_invite_link_case_team_not_found_error(
    participant_handlers: ParticipantHandlers,
    participant_registration_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
    response_mock: MagicMock,
) -> None:
    # Mock `register_invite_link_participant` to return an `Err` with `TeamNotFoundError`
    participant_registration_service_mock.register_invite_link_participant.return_value = Err(
        TeamNotFoundError()
    )

    # Call the handler
    result = await participant_handlers.create_participant(response_mock, mock_input_data_link, "example.token")

    # Check that `register_invite_link_participant` was awaited once
    participant_registration_service_mock.register_invite_link_participant.assert_awaited_once_with(mock_input_data_link, "example.token")

    # Assert the response indicates a conflict with capacity reached
    assert isinstance(result, ErrResponse)
    assert result.error == "The specified team was not found"
    response_mock.status_code = status.HTTP_409_CONFLICT