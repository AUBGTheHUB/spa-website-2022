from result import is_err
from fastapi import Response
from src.server.exception import HackathonCapacityExceededError, ParticipantNotFoundError
from src.service.participants_verification_service import ParticipantVerificationService
from starlette import status
from src.utils import JwtUtility
from src.server.schemas.response_schemas.schemas import ErrResponse, ParticipantVerifiedResponse
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData


class VerificationHandlers:
    def __init__(self, service: ParticipantVerificationService) -> None:
        self._service = service

    async def verify_participant(self, response: Response, jwt_token: str) -> ParticipantVerifiedResponse | ErrResponse:
        # Decode the JWT token using JwtUtility
        result = JwtUtility.decode_data(token=jwt_token, schema=JwtUserData)

        if is_err(result):
            # Invalid or expired JWT token
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrResponse(error=result.err_value)

        jwt_payload = result.ok_value

        if jwt_payload["is_admin"]:
            # Call for the admin participant case
            # result = await self._service.verify_admin_participant(jwt_data=jwt_payload)
            return ErrResponse(NotImplementedError())
        else:
            result = await self._service.verify_random_participant(jwt_data=jwt_payload)

        if is_err(result):
            # https://fastapi.tiangolo.com/advanced/response-change-status-code/
            if isinstance(result.err_value, ParticipantNotFoundError):
                response.status_code = status.HTTP_404_NOT_FOUND
                return ErrResponse(error="The participant was not found")

            if isinstance(result.err_value, HackathonCapacityExceededError):
                response.status_code = status.HTTP_409_CONFLICT
                return ErrResponse(error="Max hackathon capacity has been reached")

            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrResponse(error="An unexpected error occurred during the creation of Participant")

        return ParticipantVerifiedResponse(participant=result.ok_value[0], team=result.ok_value[1])
