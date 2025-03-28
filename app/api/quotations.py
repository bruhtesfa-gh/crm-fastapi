from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_lead, crud_quotation
from app.db import get_db
from app.deps import get_auth_user
from app.models import QuotationLineItem, QuotationStatus
from app.schema import MeUser
from app.schema.quotation import (  # Pydantic schemas for quotations
    QuotationCreate,
    QuotationOut,
    QuotationUpdate,
)

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.get("/", response_model=List[QuotationOut])
async def read_quotations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_auth_user),
):
    quotations = await crud_quotation.get_multi(db, skip=skip, limit=limit)
    return quotations


@router.post("/", response_model=QuotationOut)
async def create_quotation(
    quotation_in: QuotationCreate,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    lead = await crud_lead.get(db, id=quotation_in.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    from app.models import Quotation  # import the model

    line_items = [QuotationLineItem(**item.dict()) for item in quotation_in.line_items]
    # remove line_items from the quotation_in dict
    quotation_in_dict = quotation_in.dict()
    quotation_in_dict.pop("line_items")
    quotation = Quotation(
        **quotation_in_dict,
        status=QuotationStatus.DRAFT,
        total_price=sum(item.price * item.quantity for item in line_items)
    )
    quotation.line_items = line_items
    return await crud_quotation.create(db, obj_in=quotation, user_id=user.id)


@router.get("/{quotation_id}", response_model=QuotationOut)
async def read_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    quotation = await crud_quotation.get(db, id=quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.put("/{quotation_id}", response_model=QuotationOut)
async def update_quotation(
    quotation_id: int,
    quotation_in: QuotationUpdate,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    quotation = await crud_quotation.get(db, id=quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return await crud_quotation.update(
        db,
        db_obj=quotation,
        obj_in=quotation_in.dict(exclude_unset=True),
        user_id=user.id,
    )


@router.delete("/{quotation_id}")
async def delete_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    quotation = await crud_quotation.remove(db, id=quotation_id, user_id=user.id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"detail": "Quotation deleted successfully"}
