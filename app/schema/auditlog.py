from typing import Optional

from pydantic import BaseModel

from app.models import EntityType


class AuditLogCreate(BaseModel):
    entity_type: EntityType
    entity_id: int
    user_id: int
    action: str
    before_values: Optional[dict] = None
    after_values: Optional[dict] = None
    context: Optional[str] = None
