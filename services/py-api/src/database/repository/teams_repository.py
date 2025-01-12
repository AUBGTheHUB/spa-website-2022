from typing import Final, Optional, Any, Dict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from result import Result, Err, Ok
from structlog.stdlib import get_logger

from src.database.db_manager import DatabaseManager
from src.database.model.team_model import Team
from src.database.repository.base_repository import CRUDRepository
from src.server.exception import DuplicateTeamNameError, TeamNotFoundError
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

        if input_data.team_name is None:
            raise ValueError("`input_data.team_name` should NOT be None when calling this method")

        try:
            team = Team(name=input_data.team_name)
            LOG.debug("Inserting team...", team=team.dump_as_json())
            await self._collection.insert_one(document=team.dump_as_mongo_db_document(), session=session)
            return Ok(team)

        except DuplicateKeyError:
            LOG.warning("Team insertion failed due to duplicate team name", team_name=input_data.team_name)
            return Err(DuplicateTeamNameError(input_data.team_name))

        except Exception as e:
            LOG.exception("Team insertion failed due to err {}".format(e))
            return Err(e)

    async def fetch_by_id(self, obj_id: str) -> Result:
        raise NotImplementedError()

    async def fetch_all(self) -> Result:
        raise NotImplementedError()

    async def update(
        self,
        obj_id: str,
        updated_data: Dict[str, Any],
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any],
    ) -> Result[Team, TeamNotFoundError | Exception]:
        try:
            LOG.debug(f"Updating team with ObjectId={obj_id}, by setting {updated_data}.")
            result = await self._collection.find_one_and_update(
                filter={"_id": ObjectId(obj_id)},
                update={"$set": updated_data},
                return_document=ReturnDocument.AFTER,
                projection={"_id": 0},
                session=session,
            )

            if not result:
                LOG.exception(f"No updated teams because team with ObjectId={obj_id} was not found")
                return Err(TeamNotFoundError())

            LOG.debug(f"Successfully updated team with ObjectId={obj_id}")
            return Ok(Team(id=obj_id, **result))

        except Exception as e:
            LOG.exception(f"Updating team with ObjectId={obj_id} failed due to err {e}")
            return Err(e)

    async def delete(
        self, obj_id: str, session: Optional[AsyncIOMotorClientSession] = None
    ) -> Result[Team, TeamNotFoundError | Exception]:
        """
        Deletes the team which corresponds to the provided object_id
        """
        try:

            LOG.debug("Deleting team...", team_obj_id=obj_id)
            """
            According to mongodb docs result is of type _DocumentType:
            https://pymongo.readthedocs.io/en/4.8.0/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_delete
            _id is projected because ObjectID is not serializable.
            We use the Team data class to represent the deleted participant.
            """
            result = await self._collection.find_one_and_delete(filter={"_id": ObjectId(obj_id)}, projection={"_id": 0})

            """
            The result is None when the team with the specified ObjectId is not found
            """
            if result:
                return Ok(Team(id=obj_id, **result))

            return Err(TeamNotFoundError())

        except Exception as e:
            LOG.exception("Team deletion failed due to err {}".format(e))
            return Err(e)

    async def get_verified_registered_teams_count(self) -> int:
        """Returns the count of verified teams."""
        # Ignoring mypy type due to mypy err: 'Returning Any from function declared to return "int"  [no-any-return]'
        # which is not true
        try:
            count = await self._collection.count_documents({"is_verified": True})
            return int(count)
        except Exception as e:
            LOG.exception(f"Failed to count verified teams: {e}")
            return 0
