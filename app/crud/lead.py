from typing import List, Optional

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.audit import crud_audit
from app.models import EntityType, Lead
from app.schema.auditlog import AuditLogCreate
from app.schema.lead import LeadFilters


class CRUDLead:
    async def get(self, db: AsyncSession, id: int) -> Optional[Lead]:
        query = select(Lead).where(Lead.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: LeadFilters = Depends(LeadFilters),
    ) -> List[Lead]:
        query = select(Lead).offset(skip).limit(limit)
        if filters.name:
            query = query.where(Lead.name.ilike(f"%{filters.name}%"))
        if filters.email:
            query = query.where(Lead.email.ilike(f"%{filters.email}%"))
        if filters.phone:
            query = query.where(Lead.phone.ilike(f"%{filters.phone}%"))
        if filters.status:
            query = query.where(Lead.status == filters.status)
        if filters.utm_source:
            query = query.where(Lead.utm_source.ilike(f"%{filters.utm_source}%"))
        if filters.utm_medium:
            query = query.where(Lead.utm_medium.ilike(f"%{filters.utm_medium}%"))
        if filters.utm_campaign:
            query = query.where(Lead.utm_campaign.ilike(f"%{filters.utm_campaign}%"))
        if filters.utm_content:
            query = query.where(Lead.utm_content.ilike(f"%{filters.utm_content}%"))
        if filters.utm_term:
            query = query.where(Lead.utm_term.ilike(f"%{filters.utm_term}%"))
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Lead, user_id: int) -> Lead:
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        after_values = jsonable_encoder(obj_in)
        obj_audit = AuditLogCreate(
            entity_type=EntityType.LEAD,
            entity_id=obj_in.id,
            user_id=user_id,
            action="Create Lead",
            after_values=after_values,
        )
        await crud_audit.create(obj_in=obj_audit)
        return obj_in

    async def update(
        self, db: AsyncSession, *, db_obj: Lead, obj_in: dict, user_id: int
    ) -> Lead:
        before_values = jsonable_encoder(db_obj)
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        after_values = jsonable_encoder(db_obj)

        _obj_in = AuditLogCreate(
            entity_type=EntityType.LEAD,
            entity_id=db_obj.id,
            user_id=user_id,
            before_values=before_values,
            after_values=after_values,
            action="Update Lead",
        )
        await crud_audit.create(obj_in=_obj_in)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> Optional[Lead]:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
            before_values = jsonable_encoder(obj)
            _obj_in = AuditLogCreate(
                entity_type=EntityType.LEAD,
                entity_id=obj.id,
                user_id=user_id,
                before_values=before_values,
                action="Delete Lead",
            )
            await crud_audit.create(obj_in=_obj_in)
        return obj


crud_lead = CRUDLead()
