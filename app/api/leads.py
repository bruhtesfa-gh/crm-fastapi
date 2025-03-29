from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.lead import crud_lead
from app.db import get_db
from app.deps import get_auth_user 
from app.models import LeadStatus
from app.schema.lead import (  # Pydantic schemas for leads
    LeadCreate,
    LeadFilters,
    LeadOut,
    LeadPagination,
    LeadUpdate,
    LeadUpdateStatus,
)
from app.schema.user import MeUser

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("/", response_model=LeadPagination)
async def read_leads(
    skip: int = 0,
    limit: int = 100,
    filters: LeadFilters = Depends(LeadFilters),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_auth_user),
):
    leads = await crud_lead.get_multi(db, skip=skip, limit=limit, filters=filters)
    total = len(leads)
    return LeadPagination(
        items=jsonable_encoder(leads),
        total=total,
        page=skip,
        limit=limit,
        has_next=total == limit,  # if total is equal to limit, probably there next page
        has_prev=skip > 0,
    )


@router.post("/", response_model=LeadOut)
async def create_lead(
    lead_in: LeadCreate,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    from app.models import Lead  # import the model

    lead = Lead(**lead_in.dict())
    return await crud_lead.create(db, obj_in=lead, user_id=user.id)


@router.get("/{lead_id}", response_model=LeadOut)
async def read_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    lead = await crud_lead.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: int,
    lead_in: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    lead = await crud_lead.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return await crud_lead.update(
        db, db_obj=lead, obj_in=lead_in.dict(exclude_unset=True), user_id=user.id
    )


@router.put("/{lead_id}/status", response_model=LeadOut)
async def update_lead_status(
    lead_id: int,
    lead_in: LeadUpdateStatus,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    lead = await crud_lead.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead_in.status == LeadStatus.NEW:
        raise HTTPException(
            status_code=400, detail="You can't change status lead to NEW"
        )

    if lead_in.status == LeadStatus.QUALIFIED and not lead.email:
        raise HTTPException(
            status_code=400,
            detail="You can't change status lead to QUALIFIED if you don't have email",
        )
    return await crud_lead.update(
        db, db_obj=lead, obj_in=lead_in.dict(exclude_unset=True), user_id=user.id
    )


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    lead = await crud_lead.remove(db, id=lead_id, user_id=user.id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"detail": "Lead deleted successfully"}
