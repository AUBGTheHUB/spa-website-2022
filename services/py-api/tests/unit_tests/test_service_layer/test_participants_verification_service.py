import pytest

from result import Err, Ok
from unittest.mock import AsyncMock, Mock

from src.database.model.team_model import Team
from src.database.model.participant_model import Participant
from src.server.exception import HackathonCapacityExceededError, ParticipantNotFoundError, TeamNotFoundError
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData
from src.service.participants_verification_service import ParticipantVerificationService


@pytest.fixture
def p_ver_service(hackathon_service_mock: Mock) -> ParticipantVerificationService:
    return ParticipantVerificationService(hackathon_service_mock)


@pytest.mark.asyncio
async def test_verify_admin_participant_success(
    p_ver_service: ParticipantVerificationService,
    hackathon_service_mock: Mock,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: JwtUserData,
) -> None:
    # Mock not full capacity hackaton
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    # Mock update methods for team and participants repos
    team_repo_mock.update.return_value = Team(name="Test team")
    participant_repo_mock.update.return_value = Participant(
        name="Test name",
        email="Test email",
        is_admin=True,
        team_id=team_repo_mock.update.return_value.id,
    )

    hackathon_service_mock.verify_admin_participant_and_team_in_transaction.return_value = Ok(
        (participant_repo_mock.update.return_value, team_repo_mock.update.return_value)
    )

    result = await p_ver_service.verify_admin_participant(mock_input_data)

    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, tuple)
    assert isinstance(result.ok_value[0], Participant)
    assert isinstance(result.ok_value[1], Team)
    assert result.ok_value[0].name == "Test name"
    assert result.ok_value[1].name == "Test team"


@pytest.mark.asyncio
async def test_verify_admin_participant_participant_not_found_error(
    p_ver_service: ParticipantVerificationService, hackathon_service_mock: Mock, mock_input_data: JwtUserData
) -> None:
    # Mock not full capacity hackaton
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    hackathon_service_mock.verify_admin_participant_and_team_in_transaction.return_value = Err(
        ParticipantNotFoundError()
    )

    result = await p_ver_service.verify_admin_participant(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, ParticipantNotFoundError)


@pytest.mark.asyncio
async def test_verify_admin_participant_team_not_found_error(
    p_ver_service: ParticipantVerificationService, hackathon_service_mock: Mock, mock_input_data: JwtUserData
) -> None:
    # Mock not full capacity hackaton
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    hackathon_service_mock.verify_admin_participant_and_team_in_transaction.return_value = Err(TeamNotFoundError())

    result = await p_ver_service.verify_admin_participant(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, TeamNotFoundError)


@pytest.mark.asyncio
async def test_verify_admin_participant_general_exeption(
    p_ver_service: ParticipantVerificationService, hackathon_service_mock: Mock, mock_input_data: JwtUserData
) -> None:
    # Mock not full capacity hackaton
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    hackathon_service_mock.verify_admin_participant_and_team_in_transaction.return_value = Err(
        Exception("Test exception")
    )

    result = await p_ver_service.verify_admin_participant(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    str(result.err_value) == "Test exception"


@pytest.mark.asyncio
async def test_verify_admin_participant_hackaton_capacity_exceeded_error(
    p_ver_service: ParticipantVerificationService,
    hackathon_service_mock: Mock,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: JwtUserData,
) -> None:
    # Mock not full capacity hackaton
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=False)

    # Mock update methods for team and participants repos
    team_repo_mock.update.return_value = Team(name="Test team")
    participant_repo_mock.update.return_value = Participant(
        name="Test name",
        email="Test email",
        is_admin=True,
        team_id="test team id",
    )

    hackathon_service_mock.verify_admin_participant_and_team_in_transaction.return_value = Ok(
        (participant_repo_mock.update.return_value, team_repo_mock.update.return_value)
    )

    result = await p_ver_service.verify_admin_participant(mock_input_data)

    assert isinstance(result, Err)
    assert isinstance(result.err_value, HackathonCapacityExceededError)
