from typing import Union
from result import is_err
from starlette import status
from starlette.responses import Response

from src.server.exception import (
    DuplicateEmailError,
    DuplicateTeamNameError,
    HackathonCapacityExceededError,
    TeamCapacityExceededError,
    TeamNotFoundError,
)
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.server.schemas.response_schemas.schemas import (
    ParticipantRegisteredResponse,
    ErrResponse,
)
from src.service.participants_registration_service import ParticipantRegistrationService


class ParticipantHandlers:

    def __init__(self, service: ParticipantRegistrationService) -> None:
        self._service = service

    async def create_participant(
        self,
        response: Response,
        input_data: ParticipantRequestBody,
        jwt_token: Union[str, None] = None,
    ) -> ParticipantRegisteredResponse | ErrResponse:

        if input_data.is_admin and input_data.team_name:
            result = await self._service.register_admin_participant(input_data)

        elif (not input_data.is_admin) and input_data.team_name:
            result = await self._service.register_invite_link_participant(input_data, jwt_token)

        else:
            result = await self._service.register_random_participant(input_data)

        if is_err(result):
            # https://fastapi.tiangolo.com/advanced/response-change-status-code/
            if isinstance(result.err_value, DuplicateEmailError):
                response.status_code = status.HTTP_409_CONFLICT
                return ErrResponse(error="Participant with this email already exists")

            if isinstance(result.err_value, DuplicateTeamNameError):
                response.status_code = status.HTTP_409_CONFLICT
                return ErrResponse(error="Team with this name already exists")

            if isinstance(result.err_value, HackathonCapacityExceededError):
                response.status_code = status.HTTP_409_CONFLICT
                return ErrResponse(error="Max hackathon capacity has been reached")

            if isinstance(result.err_value, TeamCapacityExceededError):
                response.status_code = status.HTTP_409_CONFLICT
                return ErrResponse(error="Max team capacity has been reached")

            if isinstance(result.err_value, TeamNotFoundError):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrResponse(error="The specified team was not found")

            if isinstance(result.err_value, str):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrResponse(error=result.err_value)

            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrResponse(error="An unexpected error occurred during the creation of Participant")

        response.status_code = status.HTTP_201_CREATED
        return ParticipantRegisteredResponse(participant=result.ok_value[0], team=result.ok_value[1])
