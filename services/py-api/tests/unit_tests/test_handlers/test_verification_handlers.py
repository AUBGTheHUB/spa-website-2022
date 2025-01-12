import pytest

from typing import Any
from bson import ObjectId
from result import Err, Ok, Result
from starlette import status

from unittest.mock import Mock, MagicMock, patch

from src.utils import JwtUtility
from src.database.model.team_model import Team
from src.database.model.participant_model import Participant
from src.server.handlers.verification_handler import VerificationHandlers
from src.server.schemas.response_schemas.schemas import ErrResponse, ParticipantVerifiedResponse
from src.server.exception import HackathonCapacityExceededError, ParticipantNotFoundError, TeamNotFoundError


@pytest.fixture
def verification_handlers(participants_verification_service_mock: Mock) -> VerificationHandlers:
    return VerificationHandlers(participants_verification_service_mock)


def mock_decode_for_admin(token: str, schema: Any) -> Result[object, Exception]:
    return Ok({"is_admin": True})


@pytest.mark.asyncio
async def test_verify_participant_admin_case_success(
    participants_verification_service_mock: Mock, verification_handlers: VerificationHandlers, response_mock: MagicMock
) -> None:
    with patch.object(JwtUtility, "decode_data", new=mock_decode_for_admin):
        participants_verification_service_mock.verify_admin_participant.return_value = Ok(
            (
                Participant(
                    name="Test", email="test@gmail.com", is_admin=True, team_id=ObjectId(), email_verified=True
                ),
                Team(name="Test"),
            )
        )

        result = await verification_handlers.verify_participant(response_mock, "secret_token")

        participants_verification_service_mock.verify_admin_participant.assert_awaited_once()

        assert isinstance(result, ParticipantVerifiedResponse)
        assert result.participant.email_verified is True
        assert response_mock.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_verify_participant_admin_case_participant_not_found_error(
    participants_verification_service_mock: Mock, verification_handlers: VerificationHandlers, response_mock: MagicMock
) -> None:
    with patch.object(JwtUtility, "decode_data", new=mock_decode_for_admin):
        participants_verification_service_mock.verify_admin_participant.return_value = Err(ParticipantNotFoundError())

        result = await verification_handlers.verify_participant(response_mock, "secret_token")

        participants_verification_service_mock.verify_admin_participant.assert_awaited_once()

        assert isinstance(result, ErrResponse)
        assert result.error == "The participant was not found"
        assert response_mock.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_verify_participant_admin_case_team_not_found_error(
    participants_verification_service_mock: Mock, verification_handlers: VerificationHandlers, response_mock: MagicMock
) -> None:
    with patch.object(JwtUtility, "decode_data", new=mock_decode_for_admin):
        participants_verification_service_mock.verify_admin_participant.return_value = Err(TeamNotFoundError())

        result = await verification_handlers.verify_participant(response_mock, "secret_token")

        participants_verification_service_mock.verify_admin_participant.assert_awaited_once()

        assert isinstance(result, ErrResponse)
        assert result.error == "The team was not found"
        assert response_mock.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_verify_participant_admin_case_hackation_capacity_reached_error(
    participants_verification_service_mock: Mock, verification_handlers: VerificationHandlers, response_mock: MagicMock
) -> None:
    with patch.object(JwtUtility, "decode_data", new=mock_decode_for_admin):

        participants_verification_service_mock.verify_admin_participant.return_value = Err(
            HackathonCapacityExceededError()
        )

        result = await verification_handlers.verify_participant(response_mock, "secret_token")

        participants_verification_service_mock.verify_admin_participant.assert_awaited_once()

        assert isinstance(result, ErrResponse)
        assert result.error == "Max hackathon capacity has been reached"
        assert response_mock.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_verify_participant_admin_case_general_error(
    participants_verification_service_mock: Mock, verification_handlers: VerificationHandlers, response_mock: MagicMock
) -> None:
    with patch.object(JwtUtility, "decode_data", new=mock_decode_for_admin):

        participants_verification_service_mock.verify_admin_participant.return_value = Err(Exception())

        result = await verification_handlers.verify_participant(response_mock, "secret_token")

        participants_verification_service_mock.verify_admin_participant.assert_awaited_once()

        assert isinstance(result, ErrResponse)
        assert result.error == "An unexpected error occurred during the verification of Participant"
        assert response_mock.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
