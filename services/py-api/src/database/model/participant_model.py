from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import EmailStr

from src.database.model.base_model import Base, SerializableObjectId


@dataclass(kw_only=True)
class Participant(Base):
    """A representation of the Participant entity in Mongo. It is also the schema of how the entity should look
    like in Mongo before it is inserted"""

    name: str
    email: EmailStr
    is_admin: bool
    email_verified: bool = field(default=False)
    team_id: Optional[SerializableObjectId]
    last_sent_email: Optional[datetime] = field(default=None)

    def dump_as_mongo_db_document(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "email_verified": self.email_verified,
            "team_id": self.team_id,
            "last_sent_email": self.last_sent_email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def dump_as_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "email_verified": self.email_verified,
            "team_id": str(self.team_id) if self.team_id else None,
            "last_sent_email": self.last_sent_email.strftime("%Y-%m-%d %H:%M:%S") if self.last_sent_email else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
