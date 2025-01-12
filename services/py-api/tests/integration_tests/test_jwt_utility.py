import os
from unittest.mock import patch
from result import Err, Ok
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData
from datetime import datetime, timedelta, timezone
from src.utils import JwtUtility

sufficient_expiration_time = (datetime.now(tz=timezone.utc) + timedelta(seconds=30)).timestamp()
instant_expiration_time = (datetime.now(tz=timezone.utc)).timestamp()

CORRECT_TEST_PAYLOAD = JwtUserData(
    sub="alksdjflksd987fsidjf98sduf",
    is_admin=True,
    team_id="slkdjflkasjdflkjsdlkj",
    exp=sufficient_expiration_time,
    is_invite=True,
)

MISSING_KEY_TEST_PAYLOAD = JwtUserData(  # We need it only for testing purposes | mypy complains
    sub="alksdjflksd987fsidjf98sduf", is_admin=True, team_id="slkdjflkasjdflkjsdlkj", is_invite=True  # type: ignore[typeddict-item]
)

ADDITIONAL_KEY_TEST_PAYLOAD = JwtUserData(
    sub="alksdjflksd987fsidjf98sduf", is_admin=True, team_id="slkdjflkasjdflkjsdlkj", exp=sufficient_expiration_time, name="abcdefgji", is_invite=True  # type: ignore[typeddict-unknown-key]
)

EXPIRED_TEST_PAYLOAD = JwtUserData(
    sub="alksdjflksd987fsidjf98sduf",
    is_admin=True,
    team_id="slkdjflkasjdflkjsdlkj",
    exp=instant_expiration_time,
    is_invite=True,
)


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
def test_encode_decode_success() -> None:
    encoded_data = JwtUtility.encode_data(data=CORRECT_TEST_PAYLOAD)
    assert isinstance(encoded_data, str)

    decoded_data = JwtUtility.decode_data(token=encoded_data, schema=JwtUserData)
    assert isinstance(decoded_data, Ok)
    assert decoded_data.ok_value == CORRECT_TEST_PAYLOAD


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
def test_encode_failure_missing_keys() -> None:
    encoded_data = JwtUtility.encode_data(data=MISSING_KEY_TEST_PAYLOAD)
    assert isinstance(encoded_data, str)

    decoded_data = JwtUtility.decode_data(token=encoded_data, schema=JwtUserData)
    assert isinstance(decoded_data, Err)
    assert isinstance(decoded_data.err_value, str)
    assert decoded_data.err_value == "The decoded token does not correspond with the provided schema."


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
def test_encode_failure_additional_keys() -> None:
    encoded_data = JwtUtility.encode_data(data=ADDITIONAL_KEY_TEST_PAYLOAD)
    assert isinstance(encoded_data, str)

    decoded_data = JwtUtility.decode_data(token=encoded_data, schema=JwtUserData)
    assert isinstance(decoded_data, Err)
    assert isinstance(decoded_data.err_value, str)
    assert decoded_data.err_value == "The decoded token does not correspond with the provided schema."


@patch.dict("os.environ", {"SECRET_KEY": "abcdefghijklmnopqrst"})
def test_decode_failure_expired_token() -> None:
    encoded_data = JwtUtility.encode_data(data=EXPIRED_TEST_PAYLOAD)
    assert isinstance(encoded_data, str)

    decoded_data = JwtUtility.decode_data(token=encoded_data, schema=JwtUserData)
    assert isinstance(decoded_data, Err)
    assert isinstance(decoded_data.err_value, str)
    assert decoded_data.err_value == "The JWT token has expired."


def test_encode_decode_secret_key_mismatch() -> None:
    # Mock the SECRET_KEY environment variable for encoding
    with patch.dict(os.environ, {"SECRET_KEY": "abcdefghijklmnopqrst"}):
        encoded_data = JwtUtility.encode_data(data=CORRECT_TEST_PAYLOAD)
        assert isinstance(encoded_data, str)  # Verify token is a string

    # Mock a different SECRET_KEY environment variable for decoding
    with patch.dict(os.environ, {"SECRET_KEY": "tsrqponmlkjihgfedcab"}):
        decoded_data = JwtUtility.decode_data(token=encoded_data, schema=JwtUserData)
        assert isinstance(decoded_data, Err)  # Ensure the result is an error object
        assert isinstance(decoded_data.err_value, str)  # Error value is a string
        assert decoded_data.err_value == "The JWT token has invalid signature."
