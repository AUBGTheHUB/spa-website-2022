import datetime
from os import environ
from typing import Any, Callable, Dict
from unittest.mock import patch
from httpx import AsyncClient
import pytest
from src.utils import JwtUtility
from tests.integration_tests.conftest import PARTICIPANT_ENDPOINT_URL


@pytest.mark.asyncio
async def test_create_random_participant(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    random_participant_body = generate_participant_request_body()
    resp = await create_test_participant(participant_body=random_participant_body)
    assert resp.status_code == 201

    resp_json = resp.json()

    assert resp_json["participant"]["name"] == "testtest"
    assert resp_json["participant"]["email"] == "testtest@test.com"
    assert resp_json["participant"]["is_admin"] is False
    assert resp_json["participant"]["email_verified"] is False
    assert resp_json["participant"]["team_id"] is None
    assert resp_json["team"] is None


@pytest.mark.asyncio
async def test_create_random_participant_email_already_exists(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    random_participant_body = generate_participant_request_body()
    await create_test_participant(participant_body=random_participant_body)
    resp = await create_test_participant(participant_body=random_participant_body)
    assert resp.status_code == 409

    resp_json = resp.json()

    assert resp_json["error"] == "Participant with this email already exists"


@pytest.mark.asyncio
async def test_create_admin_participant_no_team_name(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    is_admin_true_body = generate_participant_request_body(is_admin=True)
    resp = await create_test_participant(participant_body=is_admin_true_body)
    assert resp.status_code == 422

    resp_json = resp.json()

    assert resp_json["detail"][0]["msg"] == "Value error, Field `team_name` is required when `is_admin=True`"


@pytest.mark.asyncio
async def test_create_random_participant_missing_required_fields(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    missing_req_fields_body = generate_participant_request_body(name=None)
    resp = await create_test_participant(participant_body=missing_req_fields_body)
    assert resp.status_code == 422

    resp_json = resp.json()

    assert resp_json["detail"][0]["type"] == "missing"
    assert resp_json["detail"][0]["msg"] == "Field required"


@pytest.mark.asyncio
async def test_create_admin_participant(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(is_admin=True, team_name="testteam")
    resp = await create_test_participant(participant_body=admin_participant_body)
    assert resp.status_code == 201

    resp_json = resp.json()

    assert resp_json["participant"]["name"] == "testtest"
    assert resp_json["participant"]["email"] == "testtest@test.com"
    assert resp_json["participant"]["is_admin"] is True
    assert resp_json["participant"]["email_verified"] is False
    assert resp_json["participant"]["team_id"] == resp_json["team"]["id"]
    assert resp_json["team"]["name"] == "testteam"
    assert resp_json["team"]["is_verified"] is False


# The following test shows the order of create operations when adding an admin participant:
# We first create the team --> create the admin
# That is why when trying to create the same admin we get the message that the team already exists.
# We tried to create a team with the same name twice and the app throws an exception in that moment.
@pytest.mark.asyncio
async def test_create_admin_participant_email_and_team_already_exists(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(is_admin=True, team_name="testteam")
    await create_test_participant(participant_body=admin_participant_body)
    resp = await create_test_participant(participant_body=admin_participant_body)
    assert resp.status_code == 409

    resp_json = resp.json()

    assert resp_json["error"] == "Team with this name already exists"


@pytest.mark.asyncio
async def test_create_admin_participant_team_already_exists(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(is_admin=True, team_name="testteam")
    existing_team_name_body = generate_participant_request_body(
        email="testtest1@test.com", is_admin=True, team_name="testteam"
    )

    await create_test_participant(participant_body=admin_participant_body)
    resp = await create_test_participant(participant_body=existing_team_name_body)
    assert resp.status_code == 409

    resp_json = resp.json()

    assert resp_json["error"] == "Team with this name already exists"


@pytest.mark.asyncio
async def test_create_admin_participant_email_already_exists(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(is_admin=True, team_name="testteam")
    existing_team_name_body = generate_participant_request_body(is_admin=True, team_name="testteam1")

    await create_test_participant(participant_body=admin_participant_body)
    resp = await create_test_participant(participant_body=existing_team_name_body)
    assert resp.status_code == 409

    resp_json = resp.json()

    assert resp_json["error"] == "Participant with this email already exists"


@patch.dict(environ, {"SECRET_AUTH_TOKEN": "OFFLINE_TOKEN"})
@pytest.mark.asyncio
async def test_delete_participant_success(
    generate_participant_request_body: Callable[..., Dict[str, Any]], async_client: AsyncClient
) -> None:

    result_1 = await async_client.post(PARTICIPANT_ENDPOINT_URL, json=generate_participant_request_body())
    result_2 = await async_client.delete(
        url=f"{PARTICIPANT_ENDPOINT_URL}/{result_1.json()["participant"]["id"]}",
        headers={"Authorization": f"Bearer {environ['SECRET_AUTH_TOKEN']}"},
    )
    assert result_2.status_code == 200

    result_2_json = result_2.json()

    assert result_2_json["participant"]["name"] == "testtest"
    assert result_2_json["participant"]["email"] == "testtest@test.com"
    assert result_2_json["participant"]["is_admin"] is False
    assert result_2_json["participant"]["email_verified"] is False
    assert result_2_json["participant"]["team_id"] is None


@patch.dict(environ, {"SECRET_AUTH_TOKEN": "OFFLINE_TOKEN"})
@pytest.mark.asyncio
async def test_delete_participant_unauthorized(async_client: AsyncClient, mock_obj_id: str) -> None:

    result = await async_client.delete(
        url=f"{PARTICIPANT_ENDPOINT_URL}/{mock_obj_id}", headers={"Authorization": "Bearer FakeToken"}
    )

    assert result.status_code == 401
    assert result.json()["detail"] == "Unauthorized"


@patch.dict(environ, {"SECRET_AUTH_TOKEN": "OFFLINE_TOKEN"})
@pytest.mark.asyncio
async def test_delete_participant_wrong_obj_id_format(async_client: AsyncClient) -> None:

    result = await async_client.delete(
        url=f"{PARTICIPANT_ENDPOINT_URL}/1", headers={"Authorization": f"Bearer {environ['SECRET_AUTH_TOKEN']}"}
    )

    assert result.status_code == 400
    assert result.json()["detail"] == "Wrong Object ID format"


@patch.dict(environ, {"SECRET_AUTH_TOKEN": "OFFLINE_TOKEN"})
@pytest.mark.asyncio
async def test_delete_participant_obj_id_doesnt_exist(async_client: AsyncClient, mock_obj_id: str) -> None:

    result = await async_client.delete(
        url=f"{PARTICIPANT_ENDPOINT_URL}/{mock_obj_id}",
        headers={"Authorization": f"Bearer {environ['SECRET_AUTH_TOKEN']}"},
    )

    assert result.status_code == 404
    assert result.json()["error"] == "Could not find the participant with the specified id"

@pytest.mark.asyncio
async def test_create_invite_link_participant(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:
    
    admin_participant_body = generate_participant_request_body(
        is_admin=True, team_name="testteam", email="testadmin@test.com"
    )
    resp_admin = await create_test_participant(participant_body=admin_participant_body)
    assert resp_admin.status_code == 201

    resp_admin_json = resp_admin.json()
    
    link_participant_body = generate_participant_request_body(is_admin=False, team_name="testteam")
    
    payload = {
    "sub": resp_admin_json["participant"]["team_id"],
    "is_admin": False,
    "team_name": "testteam",
    "team_id": resp_admin_json["team"]["id"],
    "is_invite": True,
    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }

    jwt_token = JwtUtility.encode_data(data=payload)
    
    resp_link = await create_test_participant(participant_body=link_participant_body, jwt_token=jwt_token)

    assert resp_link.status_code == 201
    
    resp_link_json = resp_link.json()

    assert resp_link_json["participant"]["name"] == "testtest"
    assert resp_link_json["participant"]["email"] == "testtest@test.com"
    assert resp_link_json["participant"]["is_admin"] is False
    assert resp_link_json["participant"]["email_verified"] is True
    assert resp_link_json["participant"]["team_id"] == resp_admin_json["participant"]["team_id"]
    assert resp_link_json["participant"]["team_id"] == resp_admin_json["team"]["id"]
    assert "created_at" in resp_link_json["participant"]
    assert "updated_at" in resp_link_json["participant"]

@pytest.mark.asyncio
async def test_create_invite_link_participant_expired_token(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(
        is_admin=True, team_name="testteam", email="testadmin@test.com"
    )
    resp_admin = await create_test_participant(participant_body=admin_participant_body)
    assert resp_admin.status_code == 201

    resp_admin_json = resp_admin.json()

    link_participant_body = generate_participant_request_body(is_admin=False, team_name="testteam")

    payload = {
        "sub": resp_admin_json["participant"]["team_id"],
        "is_admin": False,
        "team_name": "testteam",
        "team_id": resp_admin_json["team"]["id"],
        "is_invite": True,
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),  # Expired token
    }

    jwt_token = JwtUtility.encode_data(data=payload)

    resp_link = await create_test_participant(participant_body=link_participant_body, jwt_token=jwt_token)
    assert resp_link.status_code == 400

    resp_link_json = resp_link.json()
    assert resp_link_json["error"] == "The JWT token has expired."

@pytest.mark.asyncio
async def test_create_invite_link_participant_invalid_token(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    link_participant_body = generate_participant_request_body(is_admin=False, team_name="testteam")
    invalid_token = "invalid.jwt.token"

    resp_link = await create_test_participant(participant_body=link_participant_body, jwt_token=invalid_token)
    assert resp_link.status_code == 400

    resp_link_json = resp_link.json()
    assert resp_link_json["error"] == "There was a a general error while decoding the JWT token. Checks its format again."

@pytest.mark.asyncio
async def test_create_invite_link_participant_incorrect_team_name(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(
        is_admin=True, team_name="testteam", email="testadmin@test.com"
    )
    resp_admin = await create_test_participant(participant_body=admin_participant_body)
    assert resp_admin.status_code == 201

    resp_admin_json = resp_admin.json()

    link_participant_body = generate_participant_request_body(is_admin=False, team_name="wrongteam")

    payload = {
        "sub": "incorrect_team_id",
        "is_admin": False,
        "team_name": "testteam",
        "team_id": resp_admin_json["team"]["id"],
        "is_invite": True,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }

    jwt_token = JwtUtility.encode_data(data=payload)

    resp_link = await create_test_participant(participant_body=link_participant_body, jwt_token=jwt_token)
    assert resp_link.status_code == 400

    resp_link_json = resp_link.json()
    assert resp_link_json["error"] == "There is an issue with the provided team name"

@pytest.mark.asyncio
async def test_create_invite_link_participant_missing_token_fields(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(
        is_admin=True, team_name="testteam", email="testadmin@test.com"
    )
    resp_admin = await create_test_participant(participant_body=admin_participant_body)
    assert resp_admin.status_code == 201

    resp_admin_json = resp_admin.json()

    link_participant_body = generate_participant_request_body(is_admin=False, team_name="testteam")

    payload = {
        "is_admin": False,
        # Missing "team_name", "team_id", etc.
        "is_invite": True,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }

    jwt_token = JwtUtility.encode_data(data=payload)

    resp_link = await create_test_participant(participant_body=link_participant_body, jwt_token=jwt_token)
    assert resp_link.status_code == 400

    resp_link_json = resp_link.json()
    assert resp_link_json["error"] == "The decoded token does not correspond with the provided schema."

@pytest.mark.asyncio
async def test_create_invite_link_duplicate_participant(
    create_test_participant: Callable[..., Dict[str, Any]],
    generate_participant_request_body: Callable[..., Dict[str, Any]],
) -> None:

    admin_participant_body = generate_participant_request_body(
        is_admin=True, team_name="testteam", email="testadmin@test.com"
    )
    resp_admin = await create_test_participant(participant_body=admin_participant_body)
    assert resp_admin.status_code == 201

    resp_admin_json = resp_admin.json()

    link_participant_body = generate_participant_request_body(is_admin=False, team_name="testteam")

    payload = {
        "sub": resp_admin_json["participant"]["team_id"],
        "is_admin": False,
        "team_name": "testteam",
        "team_id": resp_admin_json["team"]["id"],
        "is_invite": True,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }

    jwt_token = JwtUtility.encode_data(data=payload)

    # Create the participant
    resp_link_1 = await create_test_participant(participant_body=link_participant_body, jwt_token=jwt_token)
    assert resp_link_1.status_code == 201

    # Attempt to create the same participant again
    resp_link_2 = await create_test_participant(participant_body=link_participant_body, jwt_token=jwt_token)
    assert resp_link_2.status_code == 409

    resp_link_2_json = resp_link_2.json()
    assert resp_link_2_json["error"] == "Participant with this email already exists"
