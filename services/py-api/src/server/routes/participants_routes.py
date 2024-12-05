from fastapi import APIRouter, Depends
from starlette.responses import Response

from src.server.routes.dependency_factory import _h_service
from src.server.handlers.participants_handlers import ParticipantHandlers
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.server.schemas.response_schemas.schemas import (
    ParticipantRegisteredResponse,
    ErrResponse,
    ParticipantDeletedResponse,
)
from src.service.hackathon_service import HackathonService
from src.service.participants_registration_service import ParticipantRegistrationService

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
participants_router = APIRouter(prefix="/hackathon/participants")


def _p_reg_service(
    h_service: HackathonService = Depends(_h_service),
) -> ParticipantRegistrationService:
    return ParticipantRegistrationService(h_service)


def _handler(p_service: ParticipantRegistrationService = Depends(_p_reg_service)) -> ParticipantHandlers:
    return ParticipantHandlers(p_service)


# https://fastapi.tiangolo.com/advanced/additional-responses/
@participants_router.post(
    "", status_code=201, responses={201: {"model": ParticipantRegisteredResponse}, 409: {"model": ErrResponse}}
)
async def create_participant(
    response: Response, input_data: ParticipantRequestBody, handler: ParticipantHandlers = Depends(_handler)
) -> ParticipantRegisteredResponse | ErrResponse:
    return await handler.create_participant(response, input_data)


@participants_router.delete(
    "/{participant_id}",
    status_code=200,
    responses={200: {"model": ParticipantDeletedResponse}, 404: {"model": ErrResponse}},
)
async def delete_participant(
    response: Response, participant_id: str, handler: ParticipantHandlers = Depends(_handler)
) -> ParticipantDeletedResponse | ErrResponse:
    return await handler.delete_participant(response, participant_id)
