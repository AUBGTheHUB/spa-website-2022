from typing import Any
from fastapi import APIRouter, Response, Depends
from src.server.handlers.verification_handler import VerificationHandlers
from src.server.schemas.response_schemas.schemas import ErrResponse, ParticipantVerifiedResponse
from src.service.participants_verification_service import ParticipantVerificationService
from src.service.hackathon_service import HackathonService
from src.server.routes.dependency_factory import _h_service

verification_router = APIRouter(prefix="/hackathon/participants/verify")


def _p_verify_service(h_service: HackathonService = Depends(_h_service)) -> ParticipantVerificationService:
    return ParticipantVerificationService(h_service)


def _handler(p_verify_service: ParticipantVerificationService = Depends(_p_verify_service)) -> VerificationHandlers:
    return VerificationHandlers(p_verify_service)


@verification_router.patch(
    "",
    status_code=200,
    responses={200: {"model": ParticipantVerifiedResponse}, 404: {"model": ErrResponse}},
)
async def verify_participant(
    response: Response, jwt_token: str, _handler: VerificationHandlers = Depends(_handler)
) -> Any:
    return await _handler.verify_participant(response=response, jwt_token=jwt_token)
