# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Lead, LeadStatus
from pydantic import BaseModel, EmailStr, validator

app = FastAPI(title="Async CRM Backend")

# Pydantic schema for input validation
class LeadCreate(BaseModel):
    name: str
    email: EmailStr | None = None  # Optional email, but business rules can enforce its presence later
    phone: str | None = None

    @validator("email")
    def email_must_be_present_for_qualification(cls, v, values):
        # Custom business logic can be applied here if needed
        return v

@app.post("/leads/", response_model=LeadCreate, status_code=status.HTTP_201_CREATED)
async def create_lead(lead: LeadCreate, db: AsyncSession = Depends(get_db)):
    new_lead = Lead(name=lead.name, email=lead.email, phone=lead.phone)
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return lead
