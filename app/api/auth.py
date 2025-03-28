from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import role_crud, user_crud
from app.crud.audit import crud_audit
from app.db import get_db
from app.models import EntityType
from app.schema import LoginResponse, MeUser, RegisterBody
from app.schema.auditlog import AuditLogCreate
from app.util.auth.mfa_auth import MFAAuth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """
    Login endpoint that handles user authentication
    """
    auth = MFAAuth(db=db, username=form_data.username, password=form_data.password)

    log_in = await auth.authenticate()
    before_values = jsonable_encoder(log_in.me)
    after_values = jsonable_encoder(log_in.me)
    obj_audit = AuditLogCreate(
        entity_type=EntityType.USER,
        entity_id=log_in.id,
        user_id=log_in.id,
        action="Login",
        before_values=before_values,
        after_values=after_values,
    )
    crud_audit.create(db, obj_in=obj_audit)
    return log_in


@router.post("/register", response_model=MeUser)
async def register(body: RegisterBody, db: AsyncSession = Depends(get_db)) -> Dict:
    """
    Register a new user
    """
    # Check if username already exists
    existing_user = await user_crud.get_by_username(db, body.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_role = await role_crud.get_by_name(db, name=body.role)
    if not db_role:
        raise HTTPException(status_code=400, detail="Role not found")

    # Create new user
    user = await user_crud.create(
        db,
        obj_in={
            "username": body.username,
            "password": body.password,  # Note: Ensure password hashing is handled in crud
            "role_id": db_role.id,
        },
    )
    before_values = jsonable_encoder(user)
    obj_audit = AuditLogCreate(
        entity_type=EntityType.USER,
        entity_id=user.id,
        user_id=user.id,
        action="Register",
        before_values=before_values,
    )
    crud_audit.create(db, obj_in=obj_audit)
    return user
