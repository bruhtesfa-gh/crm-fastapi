from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Json

from app.models import EntityType
from app.schema.user import UserInDBBase

# from app.schema.user import MeUser


class AuditLogCreate(BaseModel):
    entity_type: EntityType
    entity_id: int
    user_id: int
    action: str
    before_values: Optional[dict] = None
    after_values: Optional[dict] = None
    context: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    entity_type: EntityType
    entity_id: int
    user_id: int
    action: str
    before_values: Optional[Json] = None
    after_values: Optional[Json] = None
    context: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: UserInDBBase

    class Config:
        from_attributes = True


class AuditLogPagination(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class AuditLogFilters(BaseModel):
    entity_type: Optional[EntityType] = None
    entity_id: Optional[int] = None
    user_id: Optional[int] = None
    action: Optional[str] = None
    context: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
