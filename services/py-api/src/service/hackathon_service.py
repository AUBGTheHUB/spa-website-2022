from math import ceil
from typing import Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClientSession
from result import Err, is_err, Ok, Result

from src.database.model.participant_model import Participant
from src.database.model.team_model import Team
from src.database.repository.participants_repository import ParticipantsRepository
from src.database.repository.teams_repository import TeamsRepository
from src.database.transaction_manager import TransactionManager
from src.server.exception import (
    DuplicateTeamNameError,
    DuplicateEmailError,
    ParticipantNotFoundError,
    TeamCapacityExceededError,
    TeamNotFoundError,
)
from src.server.schemas.jwt_schemas.jwt_user_data_schema import JwtUserData
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody
from src.database.model.base_model import SerializableObjectId


class HackathonService:
    """Service layer designed to hold all business logic related to hackathon management"""

    def __init__(
        self,
        participant_repo: ParticipantsRepository,
        team_repo: TeamsRepository,
        tx_manager: TransactionManager,
    ) -> None:
        self._participant_repo = participant_repo
        self._team_repo = team_repo
        self._tx_manager = tx_manager

    async def _create_participant_and_team_in_transaction_callback(
        self, input_data: ParticipantRequestBody, session: Optional[AsyncIOMotorClientSession] = None
    ) -> Result[Tuple[Participant, Team], DuplicateEmailError | DuplicateTeamNameError | Exception]:
        """
        This method is intended to be passed as the `callback` argument to the `TransactionManager.with_transaction(...)`
        function.
        """
        team = await self._team_repo.create(input_data, session)
        if is_err(team):
            return team

        participant = await self._participant_repo.create(input_data, session, team_id=team.ok_value.id)
        if is_err(participant):
            return participant

        return Ok((participant.ok_value, team.ok_value))

    async def create_participant_and_team_in_transaction(
        self, input_data: ParticipantRequestBody
    ) -> Result[Tuple[Participant, Team], DuplicateEmailError | DuplicateTeamNameError | Exception]:
        """Creates a participant and team in a transactional manner. The participant is added to the team created. If
        any of the db operations: creation of a Team obj, creation of a Participant obj fails, the whole operation
        fails, and no permanent changes are made to the database."""
        return await self._tx_manager.with_transaction(
            self._create_participant_and_team_in_transaction_callback, input_data
        )

    async def create_random_participant(
        self, input_data: ParticipantRequestBody
    ) -> Result[Tuple[Participant, None], DuplicateEmailError | Exception]:

        result = await self._participant_repo.create(input_data)

        if is_err(result):
            return result

        # As when first created, the random participant is not assigned to a team we return the team as None
        return Ok((result.ok_value, None))

    async def create_invite_link_participant(
        self, input_data: ParticipantRequestBody, decoded_jwt_token: JwtUserData
    ) -> Result[
        Tuple[Participant, None], DuplicateEmailError | TeamCapacityExceededError | TeamNotFoundError | Exception
    ]:

        # Check if team still exists - Returns an error when it doesn't
        result = await self._team_repo.fetch_by_team_name(input_data.team_name)  # type: ignore
        if is_err(result):
            return result

        # Check Team Capacity
        has_capacity = await self.check_team_capacity(decoded_jwt_token["team_id"])
        if not has_capacity:
            return Err(TeamCapacityExceededError())

        participant_result = await self._participant_repo.create(
            input_data, team_id=SerializableObjectId(decoded_jwt_token["team_id"]), email_verified=True
        )

        if is_err(participant_result):
            return participant_result

        # Return the new participant
        return Ok((participant_result.ok_value, None))

    async def check_capacity_register_admin_participant_case(self) -> bool:
        """Calculate if there is enough capacity to register a new team. Capacity is measured in max number of verified
        teams in the hackathon. This is the Capacity Check 2 from the Excalidraw 'Adding a participant workflow'"""

        # Fetch number of verified random participants
        verified_random_participants = await self._participant_repo.get_verified_random_participants_count()

        # Fetch number of verified registered teams
        verified_registered_teams = await self._team_repo.get_verified_registered_teams_count()

        # Calculate the anticipated number of teams
        number_ant_teams = verified_registered_teams + ceil(
            verified_random_participants / self._team_repo.MAX_NUMBER_OF_TEAM_MEMBERS
        )

        # Check against the hackathon capacity
        return number_ant_teams < self._team_repo.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON

    async def check_capacity_register_random_participant_case(self) -> bool:
        """Calculate if there is enough capacity to register a new random participant. Capacity is measured in max
        number of verified teams in the hackathon. This is the Capacity Check 1 from the Excalidraw 'Adding a
        participant workflow'"""

        # Fetch number of verified random participants
        verified_random_participants = await self._participant_repo.get_verified_random_participants_count()

        # Fetch number of verified registered teams
        verified_registered_teams = await self._team_repo.get_verified_registered_teams_count()

        # Calculate the anticipated number of teams if a new random participant is added
        number_ant_teams = verified_registered_teams + ceil(
            (verified_random_participants + 1) / self._team_repo.MAX_NUMBER_OF_TEAM_MEMBERS
        )

        # Check against the hackathon capacity
        return number_ant_teams <= self._team_repo.MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON

    async def check_team_capacity(self, team_id: str) -> bool:
        """Calculate if there is enough capacity to register a new participant from the invite link for his team."""

        # Fetch number of registered participants in the team
        registered_teammates = await self._participant_repo.get_number_registered_teammates(team_id)

        # Check against team capacity
        return registered_teammates + 1 <= self._team_repo.MAX_NUMBER_OF_TEAM_MEMBERS

    async def delete_participant(
        self, participant_id: str
    ) -> Result[Participant, ParticipantNotFoundError | Exception]:
        return await self._participant_repo.delete(obj_id=participant_id)

    async def delete_team(self, team_id: str) -> Result[Team, TeamNotFoundError | Exception]:
        return await self._team_repo.delete(obj_id=team_id)
