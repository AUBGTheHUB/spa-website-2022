from abc import abstractmethod, ABC
from typing import Optional, Any, Dict

from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel
from result import Result


# Across the project we use the result pattern for better error handling
# https://www.milanjovanovic.tech/blog/functional-error-handling-in-dotnet-with-the-result-pattern
# https://github.com/rustedpy/result


class CRUDRepository(ABC):
    """An Interface for CRUD operations over a particular collection in Mongo"""

    @abstractmethod
    async def create(
        self, input_data: BaseModel, session: Optional[AsyncIOMotorClientSession] = None, **kwargs: Dict[str, Any]
    ) -> Result:
        """Create a new document in a particular collection in Mongo.

        Args:
            input_data: The data to be inserted.
            session: If provided, this operation will be executed within a session context, where other related
                operations might also be running as part of a sequence. It is also used to execute the operation in a
                transaction. For more info check the `TransactionManager` class
            **kwargs: Additional keyword arguments for specific implementations.
                For example, when creating a participant, we might pass the `team_id` of the team the participant
                should be added to.
        """
        raise NotImplementedError()

    @abstractmethod
    async def fetch_by_id(self, obj_id: str) -> Result:
        # TODO The implementer should catch invalid ObjectID format
        raise NotImplementedError()

    @abstractmethod
    async def fetch_all(self) -> Result:
        raise NotImplementedError()

    @abstractmethod
    async def update(
        self,
        obj_id: str,
        updated_data: Dict[str, Any],
        session: Optional[AsyncIOMotorClientSession] = None,
        **kwargs: Dict[str, Any]
    ) -> Result:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, obj_id: str, session: Optional[AsyncIOMotorClientSession] = None) -> Result:
        raise NotImplementedError()
