import pytest
from httpx import AsyncClient
from unittest.mock import patch
from typing import Any, Callable, Dict
from datetime import datetime, timedelta, timezone

from src.utils import JwtUtility
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData

from tests.integration_tests.conftest import PARTICIPANT_ENDPOINT_URL

EXPIRED_TOKEN_DATE = (datetime.now(tz=timezone.utc)).timestamp()
VALID_TOKEN_DATE = (datetime.now(tz=timezone.utc) + timedelta(minutes=1)).timestamp()


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
@pytest.mark.asyncio
async def test_verify_participant_admin_case_success(
    generate_participant_request_body: Callable[..., Dict[str, Any]],
    create_test_participant: Callable[..., Dict[str, Any]],
    async_client: AsyncClient,
) -> None:

    admin_participant_body = generate_participant_request_body(is_admin=True, team_name="test")
    res_one = await create_test_participant(participant_body=admin_participant_body)
    res_one_json = res_one.json()

    jwt = JwtUtility.encode_data(
        data=JwtUserData(
            sub=res_one_json["participant"]["id"],
            is_admin=True,
            team_id=res_one_json["team"]["id"],
            exp=VALID_TOKEN_DATE,
            is_invite=False,
        )
    )

    res_two = await async_client.patch(url=f"{PARTICIPANT_ENDPOINT_URL}/verify?jwt_token={jwt}")

    res_two_json = res_two.json()

    assert res_two.status_code == 200

    assert res_two_json["team"]["id"] == res_one_json["team"]["id"]
    assert res_two_json["participant"]["id"] == res_one_json["participant"]["id"]
    assert res_two_json["team"]["is_verified"] is True
    assert res_two_json["participant"]["email_verified"] is True


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
@pytest.mark.asyncio
async def test_verify_participant_admin_case_when_participant_is_not_found(
    mock_obj_id: str,
    async_client: AsyncClient,
) -> None:

    jwt = JwtUtility.encode_data(
        data=JwtUserData(
            sub=mock_obj_id,
            is_admin=True,
            team_id=mock_obj_id,
            exp=VALID_TOKEN_DATE,
            is_invite=False,
        )
    )

    res_two = await async_client.patch(url=f"{PARTICIPANT_ENDPOINT_URL}/verify?jwt_token={jwt}")

    assert res_two.status_code == 404
    assert res_two.json()["error"] == "The participant was not found"


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
@pytest.mark.asyncio
async def test_verify_participant_admin_case_when_team_is_not_found(
    generate_participant_request_body: Callable[..., Dict[str, Any]],
    create_test_participant: Callable[..., Dict[str, Any]],
    mock_obj_id: str,
    async_client: AsyncClient,
) -> None:

    # Need an existing participant_id for the token but since team id is not needed, a random participant will be generated
    admin_participant_body = generate_participant_request_body(is_admin=False)
    res_one = await create_test_participant(participant_body=admin_participant_body)

    # token with existing participant_id (sub) but not existing team_id
    jwt = JwtUtility.encode_data(
        data=JwtUserData(
            sub=res_one.json()["participant"]["id"],
            is_admin=True,
            team_id=mock_obj_id,
            exp=VALID_TOKEN_DATE,
            is_invite=False,
        )
    )

    res_two = await async_client.patch(url=f"{PARTICIPANT_ENDPOINT_URL}/verify?jwt_token={jwt}")

    res_two_json = res_two.json()
    assert res_two.status_code == 404
    assert res_two_json["error"] == "The team was not found"


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
@pytest.mark.asyncio
async def test_verify_participant_admin_case_expired_token(
    generate_participant_request_body: Callable[..., Dict[str, Any]],
    create_test_participant: Callable[..., Dict[str, Any]],
    async_client: AsyncClient,
) -> None:

    # We would like to have existing participant_id and team_id for the token
    admin_participant_body = generate_participant_request_body(is_admin=True, team_name="test")
    res_one = await create_test_participant(participant_body=admin_participant_body)

    # token with existing participant_id (sub) and team_id but with passed expiration date
    jwt = JwtUtility.encode_data(
        data=JwtUserData(
            sub=res_one.json()["participant"]["id"],
            is_admin=True,
            team_id=res_one.json()["team"]["id"],
            exp=EXPIRED_TOKEN_DATE,
            is_invite=False,
        )
    )

    invalid_token_result = await async_client.patch(url=f"{PARTICIPANT_ENDPOINT_URL}/verify?jwt_token={jwt}")

    assert invalid_token_result.status_code == 400
    assert invalid_token_result.json()["error"] == "The JWT token has expired."
