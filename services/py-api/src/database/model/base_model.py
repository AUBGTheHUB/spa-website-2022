from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic.json_schema import WithJsonSchema

from src.database.model.json_serializer import Serializer

SerializableObjectId = Annotated[ObjectId, WithJsonSchema({"type": "string", "format": "objectid"})]
"""As the original Mongo ObjectID is not json serializable this is needed to represent the ObjectID as a string in API
responses and OpenAPI documentation generated by FastAPI using the Pydantic Models. If we use the default one, the
Swagger page will throw an error because it cannot serialize the standard Mongo ObjectID"""


# https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses ans with 150 up votes
# https://www.trueblade.com/blogs/news/python-3-10-new-dataclass-features
@dataclass(kw_only=True)
class Base(Serializer, ABC):
    _id: SerializableObjectId = field(default_factory=lambda: ObjectId())
    """This is with underscore as MongoDB expects it like this. We create the ID on demand in order to return the whole
    object and have type safe attributes when used as a return type of a function
    https://www.mongodb.com/docs/languages/python/pymongo-driver/current/write/insert/#the-_id-field"""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def id(self) -> SerializableObjectId:
        return self._id
