from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from pydantic import EmailStr

from src.database.model.base_model import Base, SerializableObjectId


@dataclass(kw_only=True)
class Participant(Base):
    name: str
    email: EmailStr
    is_admin: bool
    email_verified: bool = field(default=False)
    team_id: Optional[SerializableObjectId]

    def dump_as_mongo_db_document(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "email_verified": self.email_verified,
            "team_id": self.team_id,
        }

    def dump_as_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "email_verified": self.email_verified,
            "team_id": str(self.team_id),
        }
