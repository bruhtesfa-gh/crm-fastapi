from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_lead, crud_quotation
from app.db import get_db
from app.deps import get_auth_user, user_role_check
from app.models import LeadStatus, QuotationLineItem, QuotationStatus
from app.schema import MeUser
from app.schema.quotation import (  # Pydantic schemas for quotations
    QuotationCreate,
    QuotationFilters,
    QuotationOut,
    QuotationPagination,
    QuotationUpdate,
    QuotationUpdateStatus,
)
from app.util.email.index import render_invoice_html, send_email

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.get("/", response_model=QuotationPagination)
async def read_quotations(
    skip: int = 0,
    limit: int = 100,
    filters: QuotationFilters = Depends(QuotationFilters),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_auth_user),
):
    quotations = await crud_quotation.get_multi(
        db, skip=skip, limit=limit, filters=filters
    )
    total = len(quotations)
    return QuotationPagination(
        items=jsonable_encoder(quotations),
        total=total,
        page=skip,
        limit=limit,
        has_next=total == limit,  # if total is equal to limit, probably there next page
        has_prev=skip > 0,
    )


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
        total_price=sum(item.price * item.quantity for item in line_items),
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


@router.put("/{quotation_id}/line-items", response_model=QuotationOut)
async def update_quotation_line_items(
    quotation_id: int,
    quotation_in: QuotationUpdate,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    quotation = await crud_quotation.get(db, id=quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    # check if the quotation is in draft status
    if quotation.status != QuotationStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Quotation is not in draft status, current status: {quotation.status.value}",
        )

    # check all line_items in quotation_in are in quotation.line_items
    for item in quotation_in.line_items:
        if item.id not in [line_item.id for line_item in quotation.line_items]:
            raise HTTPException(status_code=404, detail="Line item not found")

    return await crud_quotation.update_line_items(
        db,
        db_obj=quotation,
        obj_in=quotation_in.dict(exclude_unset=True),
        user_id=user.id,
    )


@router.put("/{quotation_id}/status", response_model=QuotationOut)
async def update_quotation_status(
    quotation_id: int,
    quotation_in: QuotationUpdateStatus,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    quotation = await crud_quotation.get(db, id=quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    statuses = [status.value for status in QuotationStatus]

    current_status_index = statuses.index(quotation.status.value)
    new_status_index = statuses.index(quotation_in.status.value)

    # check if the new status dose not backtrack
    if new_status_index < current_status_index:
        raise HTTPException(
            status_code=400,
            detail=f"Quotation status cannot be changed from {quotation.status.value}"
            f" to {quotation_in.status.value}",
        )

    if current_status_index == new_status_index:
        raise HTTPException(
            status_code=400,
            detail=f"Quotation status is already {quotation_in.status.value}",
        )

    # check if the new status is one step ahead of the current status
    if (
        quotation_in.status.value
        not in [QuotationStatus.REJECTED.value, QuotationStatus.ACCEPTED.value]
        and new_status_index > current_status_index + 1
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Quotation status cannot be changed from {quotation.status.value}"
            f" to {quotation_in.status.value}",
        )

    if (
        quotation_in.status.value
        in [QuotationStatus.REJECTED.value, QuotationStatus.ACCEPTED.value]
        and quotation.status.value != QuotationStatus.SENT.value
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Quotation status cannot be changed from {quotation.status.value} "
            f"to {quotation_in.status.value}",
        )

    # check if the new status is APPROVED it needs manager approval
    if quotation_in.status.value == QuotationStatus.APPROVED.value:
        user_role_check(["Manager"], user)

    return await crud_quotation.update(
        db,
        db_obj=quotation,
        obj_in=quotation_in.dict(exclude_unset=True),
        user_id=user.id,
    )


@router.post("/{quotation_id}/send", response_model=None)
async def send_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user: MeUser = Depends(get_auth_user),
):
    quotation = await crud_quotation.get(db, id=quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    lead = await crud_lead.get(db, id=quotation.lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if quotation.status.value != QuotationStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Quotation is not approved")

    if lead.email is None or lead.status.value != LeadStatus.QUALIFIED.value:
        raise HTTPException(status_code=400, detail="Lead is not qualified")
    html = render_invoice_html(
        {"lead_name": lead.name, **quotation.__dict__}, "invoice_template.html"
    )
    response = send_email("Your Invoice #3", lead.email, html)
    if response["status"] == "error":
        raise HTTPException(status_code=400, detail=response["message"])
    updated_quotation = await crud_quotation.update(
        db,
        db_obj=quotation,
        obj_in={"status": QuotationStatus.SENT.value},
        user_id=user.id,
    )
    # send email to the client
    return {"detail": "Quotation sent successfully", "quotation": updated_quotation}


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
