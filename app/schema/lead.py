from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import LeadStatus


class Phone(BaseModel):
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")


class LeadBase(Phone):
    name: str
    email: Optional[EmailStr] = None
    status: LeadStatus
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


class LeadCreate(Phone):
    name: str
    email: Optional[EmailStr] = None
    status: LeadStatus = LeadStatus.NEW
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


class LeadUpdate(Phone):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


class LeadUpdateStatus(BaseModel):
    status: LeadStatus


class LeadOut(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
