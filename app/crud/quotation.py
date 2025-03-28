from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.audit import crud_audit
from app.models import EntityType, Quotation
from app.schema.auditlog import AuditLogCreate


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
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Quotation]:
        query = (
            select(Quotation)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Quotation.line_items))
        )
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
        crud_audit.create(db, obj_in=_obj_in)
        q = await self.get(db, obj_in.id)
        return q if q else obj_in

    async def update(
        self, db: AsyncSession, *, db_obj: Quotation, obj_in: dict, user_id: int
    ) -> Quotation:
        before_values = jsonable_encoder(db_obj)
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        after_values = jsonable_encoder(db_obj)
        _obj_in = AuditLogCreate(
            entity_type=EntityType.QUOTATION,
            entity_id=db_obj.id,
            user_id=user_id,
            action="Update Quotation",
            before_values=before_values,
            after_values=after_values,
        )
        crud_audit.create(db, obj_in=_obj_in)
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
            crud_audit.create(db, obj_in=_obj_in)
        return obj


crud_quotation = CRUDQuotation()
