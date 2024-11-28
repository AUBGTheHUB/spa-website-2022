from typing import Final, Optional, Any, Dict

from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError
from result import Result, Err, Ok
from structlog.stdlib import get_logger

from src.database.db_manager import DatabaseManager
from src.database.model.team_model import Team
from src.database.repository.base_repository import CRUDRepository
from src.server.exception import DuplicateTeamNameError
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody

LOG = get_logger()


class TeamsRepository(CRUDRepository):
    MAX_NUMBER_OF_TEAM_MEMBERS: Final[int] = 6
    MAX_NUMBER_OF_VERIFIED_TEAMS_IN_HACKATHON: Final[int] = 12

    def __init__(self, db_manager: DatabaseManager, collection_name: str) -> None:
        self._collection = db_manager.get_collection(collection_name)

    async def create(
        self,
        input_data: ParticipantRequestBody,
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any],
    ) -> Result[Team, DuplicateTeamNameError | Exception]:
        """
        If the operation is not happening in a transactional context, we do not pass an explicit
        session to this method, this way the session in the parameters of this function will be
        None. Read more about implicit and explicit sessions here:
        https://github.com/mongodb/specifications/blob/master/source/sessions/driver-sessions.md
        """
        session_id = session.session_id["id"].hex() if session else None

        try:
            team = Team(name=input_data.team_name)
            LOG.debug("Inserting team...", team=team.dump_as_json(), session_id=session_id)
            await self._collection.insert_one(document=team.dump_as_mongo_db_document(), session=session)
            return Ok(team)

        except DuplicateKeyError:
            LOG.warning(
                "Team insertion failed due to duplicate team name",
                team_name=input_data.team_name,
                session_id=session_id,
            )
            return Err(DuplicateTeamNameError(input_data.team_name))

        except Exception as e:
            LOG.exception(f"Team insertion failed due to err {e}", session_id=session_id)
            return Err(e)

    async def fetch_by_id(self, obj_id: str) -> Result:
        raise NotImplementedError()

    async def fetch_all(self) -> Result:
        raise NotImplementedError()

    async def update(
        self,
        obj_id: str,
        input_data: BaseModel,
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any],
    ) -> Result:
        raise NotImplementedError()

    async def delete(self, obj_id: str, session: Optional[AsyncIOMotorClientSession] = None) -> Result:
        raise NotImplementedError()

    async def get_verified_registered_teams_count(self) -> int:
        """Returns the count of verified teams."""
        # Ignoring mypy type due to mypy err: 'Returning Any from function declared to return "int"  [no-any-return]'
        # which is not true
        return await self._collection.count_documents({"is_verified": True})  # type: ignore
