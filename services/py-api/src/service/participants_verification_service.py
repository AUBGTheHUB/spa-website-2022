from typing import Tuple
from result import Err, Result
from src.database.model.participant_model import Participant
from src.database.model.team_model import Team
from src.server.exception import HackathonCapacityExceededError
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData
from src.service.hackathon_service import HackathonService


class ParticipantVerificationService:
    """Service layer responsible for handling the business logic when verifying a participant"""

    def __init__(self, hackathon_service: HackathonService) -> None:
        self._hackathon_service = hackathon_service

    async def verify_admin_participant(self, jwt_data: JwtUserData) -> Result[
        Tuple[Participant, Team],
        HackathonCapacityExceededError | Exception,
    ]:
        has_capacity = await self._hackathon_service.check_capacity_register_admin_participant_case()
        if not has_capacity:
            return Err(HackathonCapacityExceededError())

        return await self._hackathon_service.verify_admin_participant_and_team_in_transaction(jwt_data=jwt_data)
