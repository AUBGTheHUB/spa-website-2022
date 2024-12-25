from typing import Final, Optional, Any, Dict, Mapping

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel
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
        self._db_manager = db_manager

    async def create(
        self,
        input_data: ParticipantRequestBody,
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any]
    ) -> Result[Team, DuplicateTeamNameError | Exception]:

        if input_data.team_name is None:
            raise ValueError("`input_data.team_name` should NOT be None when calling this method")

        team = Team(name=input_data.team_name)

        async def db_operation() -> None:
            await self._collection.insert_one(document=team.dump_as_mongo_db_document(), session=session)

        try:
            LOG.debug("Inserting team...", team=team.dump_as_json())

            # The `TransactionManager.with_transaction` method provides the session and has a built-in retry
            # mechanism
            if session:
                await db_operation()
            else:
                await self._db_manager.retry_db_operation(db_operation, is_read_operation=False)

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
        input_data: BaseModel,
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any]
    ) -> Result:
        raise NotImplementedError()

    async def delete(
        self, obj_id: str, session: Optional[AsyncIOMotorClientSession] = None
    ) -> Result[Team, TeamNotFoundError | Exception]:
        """
        Deletes the team which corresponds to the provided object_id
        """

        async def db_operation() -> Mapping[str, Any]:
            # According to mongodb docs result is of type _DocumentType:
            # https://pymongo.readthedocs.io/en/4.8.0/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_delete
            # _id is projected because ObjectID is not serializable.
            #  We use the Team data class to represent the deleted team.
            delete_result = await self._collection.find_one_and_delete(
                filter={"_id": ObjectId(obj_id)}, projection={"_id": 0}
            )
            # Ignoring mypy type due to mypy err: 'Returning Any from function declared to return "int"  [no-any-return]'
            # which is not true
            return delete_result  # type: ignore

        try:

            LOG.debug("Deleting team...", team_obj_id=obj_id)

            # The `TransactionManager.with_transaction` method provides the session and has a built-in retry
            # mechanism
            if session:
                result = await db_operation()
            else:
                result = await self._db_manager.retry_db_operation(db_operation, is_read_operation=False)

            # The result is None when the team with the specified ObjectId is not found
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
        async def db_operation() -> int:
            return await self._collection.count_documents({"is_verified": True})  # type: ignore

        return await self._db_manager.retry_db_operation(db_operation, is_read_operation=True)
