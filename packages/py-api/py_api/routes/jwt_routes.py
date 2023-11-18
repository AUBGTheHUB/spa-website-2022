from typing import Dict, Tuple

from fastapi import APIRouter, Request
from py_api.controllers import VerificationController as c

router = APIRouter(prefix="/hackathon/verify")


@router.get("", response_model=Tuple[Dict[str, str], int])
def verify_user_route(verification_token: str) -> Tuple[Dict[str, str], int]:
    return c.verify_participant(verification_token)
