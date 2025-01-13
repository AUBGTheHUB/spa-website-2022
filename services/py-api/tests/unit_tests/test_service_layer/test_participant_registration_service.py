from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest
from result import Ok, Err

from src.database.model.participant_model import Participant
from src.database.model.team_model import Team
from src.server.exception import DuplicateTeamNameError, DuplicateEmailError, HackathonCapacityExceededError, TeamCapacityExceededError
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.service.participants_registration_service import ParticipantRegistrationService
from src.utils import JwtUtility


@pytest.fixture
def p_reg_service(hackathon_service_mock: Mock) -> ParticipantRegistrationService:
    return ParticipantRegistrationService(hackathon_service_mock)


@pytest.mark.asyncio
async def test_register_admin_participant_success(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    # Mock successful `create` responses for team and participant. These are the operations inside the passed callback
    # to with_transaction
    team_repo_mock.create.return_value = Team(name=mock_input_data.team_name)
    participant_repo_mock.create.return_value = Participant(
        name=mock_input_data.name,
        email=mock_input_data.email,
        is_admin=True,
        team_id=team_repo_mock.create.return_value.id,
    )

    hackathon_service_mock.create_participant_and_team_in_transaction.return_value = Ok(
        (participant_repo_mock.create.return_value, team_repo_mock.create.return_value)
    )

    # Call the function under test
    result = await p_reg_service.register_admin_participant(mock_input_data)

    # Check that the result is an `Ok` containing both the participant and team objects
    assert isinstance(result, Ok)
    assert isinstance(result.ok_value, tuple)
    assert isinstance(result.ok_value[0], Participant)
    assert isinstance(result.ok_value[1], Team)


@pytest.mark.asyncio
async def test_register_admin_participant_duplicate_team_name_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    # Mock `create_participant_and_team_in_transaction` to return an `Err` for duplicate team name
    hackathon_service_mock.create_participant_and_team_in_transaction.return_value = Err(
        DuplicateTeamNameError(mock_input_data.team_name)
    )

    # Call the function under test
    result = await p_reg_service.register_admin_participant(mock_input_data)

    # Check that the result is an `Err` with `DuplicateTeamNameError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateTeamNameError)
    assert str(result.err_value) == mock_input_data.team_name


@pytest.mark.asyncio
async def test_register_admin_participant_duplicate_email_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    # Mock `create_participant_and_team_in_transaction` to return an `Err` for duplicate email err
    hackathon_service_mock.create_participant_and_team_in_transaction.return_value = Err(
        DuplicateEmailError(mock_input_data.email)
    )

    # Call the function under test
    result = await p_reg_service.register_admin_participant(mock_input_data)

    # Check that the result is an `Err` with `DuplicateTeamNameError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    assert str(result.err_value) == mock_input_data.email


@pytest.mark.asyncio
async def test_register_admin_participant_general_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=True)

    # Mock `create_participant_and_team_in_transaction` to raise a general exception
    hackathon_service_mock.create_participant_and_team_in_transaction.return_value = Err(Exception("Test error"))

    # Call the function under test
    result = await p_reg_service.register_admin_participant(mock_input_data)

    # Verify the result is an `Err` containing a general Exception
    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    assert str(result.err_value) == "Test error"


@pytest.mark.asyncio
async def test_register_admin_participant_with_hackathon_cap_exceeded(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    team_repo_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock full hackathon
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=False)

    # Everything else is as expected
    team_repo_mock.create.return_value = Team(name=mock_input_data.team_name)
    participant_repo_mock.create.return_value = Participant(
        name=mock_input_data.name,
        email=mock_input_data.email,
        is_admin=True,
        team_id=team_repo_mock.create.return_value.id,
    )

    hackathon_service_mock.create_participant_and_team_in_transaction.return_value = Ok(
        (participant_repo_mock.create.return_value, team_repo_mock.create.return_value)
    )

    # Call the function under test
    result = await p_reg_service.register_admin_participant(mock_input_data)

    # Check that the result is an `Err` of type HackathonCapacityExceededError
    assert isinstance(result, Err)
    assert isinstance(result.err_value, HackathonCapacityExceededError)


@pytest.mark.asyncio
async def test_register_admin_participant_order_of_operations(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data: ParticipantRequestBody,
) -> None:
    # Mock full hackathon
    hackathon_service_mock.check_capacity_register_admin_participant_case = AsyncMock(return_value=False)

    # Mock `create_participant_and_team_in_transaction` to raise a general exception
    # This is in order to show that we should return the first faced err and that we check first the hackathon capacity
    # It should have no effect to the expected result of the test
    hackathon_service_mock.create_participant_and_team_in_transaction.return_value = Err(Exception("Test error"))

    # Call the function under test
    result = await p_reg_service.register_admin_participant(mock_input_data)

    # Check that the result is an `Err` of type HackathonCapacityExceededError
    assert isinstance(result, Err)
    assert isinstance(result.err_value, HackathonCapacityExceededError)

@pytest.mark.asyncio
async def test_register_random_participant_success(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_random_participant_case = AsyncMock(return_value=True)

    # Mock successful `create` responses for team and participant. These are the operations inside the passed callback
    # to with_transaction
    participant_repo_mock.create.return_value = Participant(
        name=mock_input_data_random.name,
        email=mock_input_data_random.email,
        is_admin=False,
        team_id=None,
    )

    hackathon_service_mock.create_random_participant.return_value = Ok((participant_repo_mock.create.return_value, None))

    # Call the function under test
    result = await p_reg_service.register_random_participant(mock_input_data_random)

    # Validate that the result is an `Ok` instance containing the created participant
    assert isinstance(result, Ok)
    participant, team = result.ok_value  # Unpack the tuple

    assert isinstance(participant, Participant)
    assert participant.name == mock_input_data_random.name
    assert participant.email == mock_input_data_random.email
    assert not participant.is_admin  # Ensure it is not an admin 
    assert team is None # Ensure second element is None since teams are assigned later
    
@pytest.mark.asyncio
async def test_register_random_participant_duplicate_email_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_random_participant_case = AsyncMock(return_value=True)

    # Mock `create_random_participant` to return an `Err` for duplicate email err
    hackathon_service_mock.create_random_participant.return_value = Err(
        DuplicateEmailError(mock_input_data_random.email)
    )

    # Call the function under test
    result = await p_reg_service.register_random_participant(mock_input_data_random)

    # Check that the result is an `Err` with `DuplicateTeamNameError`
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    assert str(result.err_value) == mock_input_data_random.email

@pytest.mark.asyncio
async def test_register_random_participant_general_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
) -> None:
    # Mock not full hackathon
    hackathon_service_mock.check_capacity_register_random_participant_case = AsyncMock(return_value=True)

    # Mock `create_random_participant` to raise a general exception
    hackathon_service_mock.create_random_participant.return_value = Err(Exception("Test error"))

    # Call the function under test
    result = await p_reg_service.register_random_participant(mock_input_data_random)

    # Verify the result is an `Err` containing a general Exception
    assert isinstance(result, Err)
    assert isinstance(result.err_value, Exception)
    assert str(result.err_value) == "Test error"

@pytest.mark.asyncio
async def test_register_random_participant_with_hackathon_cap_exceeded(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    participant_repo_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
) -> None:
    # Mock full hackathon
    hackathon_service_mock.check_capacity_register_random_participant_case = AsyncMock(return_value=False)

    # Everything else is as expected
    participant_repo_mock.create.return_value = Participant(
        name=mock_input_data_random.name,
        email=mock_input_data_random.email,
        is_admin=False,
        team_id=None,
    )

    hackathon_service_mock.create_random_participant.return_value = Ok(participant_repo_mock.create.return_value)

    # Call the function under test
    result = await p_reg_service.register_random_participant(mock_input_data_random)

    # Check that the result is an `Err` of type HackathonCapacityExceededError
    assert isinstance(result, Err)
    assert isinstance(result.err_value, HackathonCapacityExceededError)

@pytest.mark.asyncio
async def test_register_random_participant_order_of_operations(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data_random: ParticipantRequestBody,
) -> None:
    # Mock full hackathon
    hackathon_service_mock.check_capacity_register_random_participant_case = AsyncMock(return_value=False)

    # Mock `create_random_participant` to raise a general exception
    # This is in order to show that we should return the first faced err and that we check first the hackathon capacity
    # It should have no effect to the expected result of the test
    hackathon_service_mock.create_random_participant.return_value = Err(Exception("Test error"))

    # Call the function under test
    result = await p_reg_service.register_random_participant(mock_input_data_random)

    # Check that the result is an `Err` of type HackathonCapacityExceededError
    assert isinstance(result, Err)
    assert isinstance(result.err_value, HackathonCapacityExceededError)

@pytest.mark.asyncio
async def test_register_invite_link_participant_success(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
) -> None:
    # Mock a valid decoded JWT token
    valid_decoded_token = {
        "sub": "user123",
        "is_admin": False,
        "team_name": mock_input_data_link.team_name,
        "team_id": "63e6b3ecf2a1234abcd56789",
        "is_invite": True,
    }

    # Mock the JwtUtility to decode the token successfully
    JwtUtility.decode_data = Mock(return_value=Ok(valid_decoded_token))

    # Mock successful creation of the participant via `create_invite_link_participant`
    hackathon_service_mock.create_invite_link_participant.return_value = Ok(
        Participant(
            name=mock_input_data_link.name,
            email=mock_input_data_link.email,
            is_admin=False,
            team_id=valid_decoded_token["team_id"],
        )
    )

    # Call the function under test
    result = await p_reg_service.register_invite_link_participant(
        input_data=mock_input_data_link, jwt_token="valid.jwt.token"
    )

    # Validate the result
    assert isinstance(result, Ok)
    participant = result.ok_value

    assert isinstance(participant, Participant)
    assert participant.name == mock_input_data_link.name
    assert participant.email == mock_input_data_link.email
    assert not participant.is_admin
    assert str(participant.team_id) == valid_decoded_token["team_id"]

@pytest.mark.asyncio
async def test_register_invite_link_participant_missing_token_error(
    p_reg_service: ParticipantRegistrationService,
    mock_input_data_link: ParticipantRequestBody,
) -> None:
    # Call the function with `jwt_token` as None
    result = await p_reg_service.register_invite_link_participant(
        input_data=mock_input_data_link, jwt_token=None
    )

    # Validate the result
    assert isinstance(result, Err)
    assert result.err_value == "JWT token is missing"

@pytest.mark.asyncio
async def test_register_invite_link_participant_jwt_decoding_error(
    p_reg_service: ParticipantRegistrationService,
    mock_input_data_link: ParticipantRequestBody,
) -> None:
    # Mock JwtUtility to return a decoding error
    JwtUtility.decode_data = Mock(return_value=Err("Invalid JWT token"))

    # Call the function
    result = await p_reg_service.register_invite_link_participant(
        input_data=mock_input_data_link, jwt_token="invalid.jwt.token"
    )

    # Validate the result
    assert isinstance(result, Err)
    assert result.err_value == "Invalid JWT token"

@pytest.mark.asyncio
async def test_register_invite_link_participant_team_name_mismatch_error(
    p_reg_service: ParticipantRegistrationService,
    mock_input_data_link: ParticipantRequestBody,
) -> None:
    # Mock a decoded token with a mismatched `team_name`
    mismatched_token = {
        "sub": "user123",
        "is_admin": False,
        "team_name": "Different Team",
        "team_id": "63e6b3ecf2a1234abcd56789",
        "is_invite": True,
    }

    # Mock JwtUtility to decode the token successfully
    JwtUtility.decode_data = Mock(return_value=Ok(mismatched_token))

    # Call the function
    result = await p_reg_service.register_invite_link_participant(
        input_data=mock_input_data_link, jwt_token="valid.jwt.token"
    )

    # Validate the result
    assert isinstance(result, Err)
    assert result.err_value == "There is an issue with the provided team name"

@pytest.mark.asyncio
async def test_register_invite_link_participant_duplicate_email_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
) -> None:
    # Mock a valid decoded JWT token
    valid_decoded_token = {
        "sub": "user123",
        "is_admin": False,
        "team_name": mock_input_data_link.team_name,
        "team_id": "63e6b3ecf2a1234abcd56789",
        "is_invite": True,
    }

    # Mock JwtUtility to decode the token successfully
    JwtUtility.decode_data = Mock(return_value=Ok(valid_decoded_token))

    # Mock `create_invite_link_participant` to return an `Err` with an instance of `DuplicateEmailError`
    hackathon_service_mock.create_invite_link_participant.return_value = Err(DuplicateEmailError(mock_input_data_link.email))

    # Call the function
    result = await p_reg_service.register_invite_link_participant(
        input_data=mock_input_data_link, jwt_token="valid.jwt.token"
    )

    # Validate the result
    assert isinstance(result, Err)
    assert isinstance(result.err_value, DuplicateEmailError)
    assert str(result.err_value) == mock_input_data_link.email

@pytest.mark.asyncio
async def test_register_invite_link_participant_team_capacity_exceeded_error(
    p_reg_service: ParticipantRegistrationService,
    hackathon_service_mock: Mock,
    mock_input_data_link: ParticipantRequestBody,
) -> None:
    # Mock a valid decoded JWT token
    valid_decoded_token = {
        "sub": "user123",
        "is_admin": False,
        "team_name": mock_input_data_link.team_name,
        "team_id": "63e6b3ecf2a1234abcd56789",
        "is_invite": True,
    }

    # Mock JwtUtility to decode the token successfully
    JwtUtility.decode_data = Mock(return_value=Ok(valid_decoded_token))

    # Mock `create_invite_link_participant` to return an `Err` with an instance of `TeamCapacityExceededError`
    hackathon_service_mock.create_invite_link_participant.return_value = Err(TeamCapacityExceededError())

    # Call the function
    result = await p_reg_service.register_invite_link_participant(
        input_data=mock_input_data_link, jwt_token="valid.jwt.token"
    )

    # Validate the result
    assert isinstance(result, Err)
    assert isinstance(result.err_value, TeamCapacityExceededError)  # Ensure it's the correct error type
