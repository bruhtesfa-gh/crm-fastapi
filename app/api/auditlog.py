from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.audit import crud_audit
from app.db import get_db
from app.deps import get_auth_user
from app.models import AuditLog
from app.schema.auditlog import AuditLogFilters, AuditLogPagination, AuditLogResponse
from app.schema.user import MeUser

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=AuditLogPagination)
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    filters: AuditLogFilters = Depends(AuditLogFilters),
    db: AsyncSession = Depends(get_db),
    current_user: MeUser = Depends(get_auth_user),
) -> AuditLogPagination:
    """
    Retrieve audit logs.
    Only accessible by Admin and Manager roles.
    """
    logs = await crud_audit.get_multi(db, skip=skip, limit=limit, filters=filters)
    return AuditLogPagination(
        items=jsonable_encoder(logs),
        total=len(logs),
        page=skip,
        limit=limit,
        has_next=len(logs) == limit,
        has_prev=skip > 0,
    )


@router.get("/{audit_id}", response_model=AuditLogResponse)
async def get_audit_log(
    audit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: MeUser = Depends(get_auth_user),
) -> AuditLog:
    """
    Retrieve a specific audit log by ID.
    Only accessible by Admin and Manager roles.
    """
    audit_log = await crud_audit.get(db, id=audit_id)
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log
