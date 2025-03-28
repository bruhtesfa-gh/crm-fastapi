import json
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.schema import AuditLogCreate


class CRUDAudit:
    async def get(self, db: AsyncSession, id: int) -> Optional[AuditLog]:
        query = select(AuditLog).where(AuditLog.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        query = select(AuditLog).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: AuditLogCreate) -> AuditLog:
        before_values = json.dumps(obj_in.before_values)
        after_values = json.dumps(obj_in.after_values)
        db_obj = AuditLog(
            **obj_in.dict(exclude={"before_values", "after_values"}),
            before_values=before_values,
            after_values=after_values
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
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
