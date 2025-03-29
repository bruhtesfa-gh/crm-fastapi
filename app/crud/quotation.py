from typing import List, Optional

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.audit import crud_audit
from app.models import EntityType, Quotation
from app.schema.auditlog import AuditLogCreate
from app.schema.quotation import QuotationFilters


class CRUDQuotation:
    async def get(self, db: AsyncSession, id: int) -> Optional[Quotation]:
        query = (
            select(Quotation)
            .where(Quotation.id == id)
            .options(selectinload(Quotation.line_items))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: QuotationFilters = Depends(QuotationFilters),
    ) -> List[Quotation]:
        query = (
            select(Quotation)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Quotation.line_items))
        )
        if filters.lead_id:
            query = query.where(Quotation.lead_id == filters.lead_id)
        if filters.status:
            query = query.where(Quotation.status == filters.status)
        if filters.price_from:
            query = query.where(Quotation.total_price >= filters.price_from)
        if filters.price_to:
            query = query.where(Quotation.total_price <= filters.price_to)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: Quotation, user_id: int
    ) -> Quotation:
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        after_values = jsonable_encoder(obj_in)
        _obj_in = AuditLogCreate(
            entity_type=EntityType.QUOTATION,
            entity_id=obj_in.id,
            user_id=user_id,
            action="Create Quotation",
            after_values=after_values,
        )
        await crud_audit.create(obj_in=_obj_in)
        q = await self.get(db, obj_in.id)
        return q if q else obj_in

    async def update_line_items(
        self, db: AsyncSession, *, db_obj: Quotation, obj_in: dict, user_id: int
    ) -> Quotation:
        before_values = jsonable_encoder(db_obj)
        # update the line items
        for item in db_obj.line_items:
            if item.id in [line_item["id"] for line_item in obj_in["line_items"]]:
                _item = next(
                    (
                        line_item
                        for line_item in obj_in["line_items"]
                        if line_item["id"] == item.id
                    ),
                    None,
                )
                for field, value in _item.items() if _item is not None else {}:
                    setattr(item, field, value)

        db_obj.total_price = sum(
            item.price * item.quantity for item in db_obj.line_items
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        after_values = jsonable_encoder(db_obj)
        _obj_in = AuditLogCreate(
            entity_type=EntityType.QUOTATION,
            entity_id=db_obj.id,
            user_id=user_id,
            action="Update Quotation Line Items",
            before_values=before_values,
            after_values=after_values,
        )
        await crud_audit.create(obj_in=_obj_in)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Quotation, obj_in: dict, user_id: int
    ) -> Quotation:
        before_values = obj_in
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        after_values = obj_in
        _obj_in = AuditLogCreate(
            entity_type=EntityType.QUOTATION,
            entity_id=db_obj.id,
            user_id=user_id,
            action="Update Quotation",
            before_values=before_values,
            after_values=after_values,
        )
        await crud_audit.create(_obj_in)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> Optional[Quotation]:
        obj = await self.get(db, id=id)
        before_values = jsonable_encoder(obj)
        if obj:
            await db.delete(obj)
            await db.commit()
            _obj_in = AuditLogCreate(
                entity_type=EntityType.QUOTATION,
                entity_id=obj.id,
                user_id=user_id,
                action="Delete Quotation",
                before_values=before_values,
            )
            await crud_audit.create(obj_in=_obj_in)
        return obj


crud_quotation = CRUDQuotation()
