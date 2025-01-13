from typing import Optional, Any, Dict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from result import Result, Ok, Err
from structlog.stdlib import get_logger

from src.database.db_manager import DatabaseManager
from src.database.model.participant_model import Participant
from src.database.repository.base_repository import CRUDRepository
from src.server.exception import DuplicateEmailError, ParticipantNotFoundError
from src.server.schemas.request_schemas.schemas import ParticipantRequestBody

LOG = get_logger()


class ParticipantsRepository(CRUDRepository):
    def __init__(self, db_manager: DatabaseManager, collection_name: str) -> None:
        self._collection = db_manager.get_collection(collection_name)

    async def fetch_by_id(self, obj_id: str) -> Result[Participant, Exception]:
        try:
            LOG.debug("Fetching participant by ObjectId...", obj_id=obj_id)

            # Query the database for the participant with the given object id
            participant = await self._collection.find_one({"_id": ObjectId(obj_id)})

            if participant is None:  # If no participant is found, return an Err
                return Err(ParticipantNotFoundError())

            return Ok(participant)

        except Exception as e:
            LOG.exception(f"Failed to fetch participant by ObjectId {obj_id} due to err {e}")
            return Err(e)

    async def fetch_all(self) -> Result:
        raise NotImplementedError()

    async def update(
        self,
        obj_id: str,
        updated_data: Dict[str, Any],
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any],
    ) -> Result[Participant, ParticipantNotFoundError | Exception]:
        try:

            LOG.debug(f"Updating participant with ObjectId={obj_id}, by setting {updated_data}.")

            # ReturnDocument.AFTER returns the updated document instead of the orignal document which is the
            # default behaviour.
            result = await self._collection.find_one_and_update(
                filter={"_id": ObjectId(obj_id)},
                update={"$set": updated_data},
                projection={"_id": 0},
                return_document=ReturnDocument.AFTER,
                session=session,
            )

            # The result is None when the participant with the specified ObjectId is not found
            if result:
                return Ok(Participant(id=obj_id, **result))

            return Err(ParticipantNotFoundError())

        except Exception as e:
            LOG.exception(f"Failed to update participant with id {obj_id} due to {e}")
            return Err(e)

    async def delete(
        self, obj_id: str, session: Optional[AsyncIOMotorClientSession] = None
    ) -> Result[Participant, ParticipantNotFoundError | Exception]:
        """
        Deletes the participant which corresponds to the provided object_id
        """
        try:

            LOG.debug("Deleting participant...", participant_obj_id=obj_id)

            # According to mongodb docs result is of type _DocumentType:
            # https://pymongo.readthedocs.io/en/4.8.0/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_delete
            # _id is projected because ObjectID is not serializable.
            # We use the Participant data class to represent the deleted participant.
            result = await self._collection.find_one_and_delete(filter={"_id": ObjectId(obj_id)}, projection={"_id": 0})

            # The result is None when the participant with the specified ObjectId is not found
            if result:
                return Ok(Participant(id=obj_id, **result))

            return Err(ParticipantNotFoundError())

        except Exception as e:
            LOG.exception("Participant deletion failed due to err {}".format(e))
            return Err(e)

    async def create(
        self,
        input_data: ParticipantRequestBody,
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any],
    ) -> Result[Participant, DuplicateEmailError | Exception]:
        try:
            participant = Participant(
                name=input_data.name,
                email=input_data.email,
                is_admin=input_data.is_admin,
                # If the team_id is passed as a kwarg the participant will be inserted in the given team
                team_id=kwargs.get("team_id"),
            )
            LOG.debug("Inserting participant...", participant=participant.dump_as_json())
            await self._collection.insert_one(document=participant.dump_as_mongo_db_document(), session=session)
            return Ok(participant)
        except DuplicateKeyError:
            LOG.warning("Participant insertion failed due to duplicate email", email=input_data.email)
            return Err(DuplicateEmailError(input_data.email))
        except Exception as e:
            LOG.exception("Participant insertion failed due to err {}".format(e))
            return Err(e)

    async def get_verified_random_participants_count(self) -> int:
        """Returns the count of verified participants who are not assigned to any team."""
        # Ignoring mypy type due to mypy err: 'Returning Any from function declared to return "int"  [no-any-return]'
        # which is not true
        try:
            return await self._collection.count_documents({"email_verified": True, "team_id": None})  # type: ignore
        except Exception as e:
            LOG.exception(f"Failed to count verified random participants: {e}")
            return 0
