import asyncio
import json
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import AsyncSessionLocal  # Your async session maker
from app.models import AuditLog
from app.schema import AuditLogCreate
from app.schema.auditlog import AuditLogFilters


class CRUDAudit:
    async def get(self, db: AsyncSession, id: int) -> Optional[AuditLog]:
        query = select(AuditLog).where(AuditLog.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        filters: AuditLogFilters = Depends(AuditLogFilters),
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        query = (
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            if filters.entity_type:
                query = query.where(AuditLog.entity_type == filters.entity_type)
            if filters.entity_id:
                query = query.where(AuditLog.entity_id == filters.entity_id)
            if filters.user_id:
                query = query.where(AuditLog.user_id == filters.user_id)
            if filters.action:
                query = query.where(AuditLog.action.ilike(f"%{filters.action}%"))
            if filters.context:
                query = query.where(AuditLog.context.ilike(f"%{filters.context}%"))
            if filters.date_from:
                query = query.where(AuditLog.created_at >= filters.date_from)
            if filters.date_to:
                query = query.where(AuditLog.created_at <= filters.date_to)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: AuditLogCreate) -> None:
        # Create a new session for the background task
        asyncio.create_task(self.create_async(obj_in))

    async def create_async(self, obj_in: AuditLogCreate) -> AuditLog:
        async with AsyncSessionLocal() as session:
            before_values = json.dumps(obj_in.before_values)
            after_values = json.dumps(obj_in.after_values)
            db_obj = AuditLog(
                **obj_in.model_dump(exclude={"before_values", "after_values"}),
                before_values=before_values,
                after_values=after_values,
            )
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: AuditLog, obj_in: dict
    ) -> AuditLog:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[AuditLog]:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


crud_audit = CRUDAudit()
