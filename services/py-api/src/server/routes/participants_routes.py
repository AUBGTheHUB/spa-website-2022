from typing import Union
from fastapi import APIRouter, Depends
from src.server.handlers.hackathon_handlers import HackathonManagementHandlers
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
from src.server.routes.dependency_factory import is_auth, validate_obj_id

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
participants_router = APIRouter(prefix="/hackathon/participants")


def _p_reg_service(
    h_service: HackathonService = Depends(_h_service),
) -> ParticipantRegistrationService:
    return ParticipantRegistrationService(h_service)


def _p_handler(p_service: ParticipantRegistrationService = Depends(_p_reg_service)) -> ParticipantHandlers:
    return ParticipantHandlers(p_service)


def _h_handler(
    h_service: HackathonService = Depends(_h_service),
) -> HackathonManagementHandlers:
    return HackathonManagementHandlers(h_service)


# https://fastapi.tiangolo.com/advanced/additional-responses/
@participants_router.post(
    "", status_code=201, responses={201: {"model": ParticipantRegisteredResponse}, 409: {"model": ErrResponse}}
)
async def create_participant(
    response: Response,
    input_data: ParticipantRequestBody,
    jwt_token: Union[str, None] = None,
    handler: ParticipantHandlers = Depends(_p_handler),
) -> ParticipantRegisteredResponse | ErrResponse:
    return await handler.create_participant(response, input_data, jwt_token)


@participants_router.delete(
    "/{object_id}",
    status_code=200,
    responses={200: {"model": ParticipantDeletedResponse}, 404: {"model": ErrResponse}},
    dependencies=[Depends(is_auth), Depends(validate_obj_id)],
)
async def delete_participant(
    response: Response, object_id: str, handler: HackathonManagementHandlers = Depends(_h_handler)
) -> ParticipantDeletedResponse | ErrResponse:
    return await handler.delete_participant(response, object_id)
