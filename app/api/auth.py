from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schema.index import MeUser
from app.util.auth.mfa_auth import MFAAuth
from app.models import User
from app.crud.user import user_crud
from typing import Dict

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Login endpoint that handles user authentication
    """
    auth = MFAAuth(db=db, username=form_data.username, password=form_data.password)
    return await auth.authenticate()

@router.post("/register")
async def register(
    username: str,
    password: str,
    role_id: int = 1,  # Default role_id, adjust as needed
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Register a new user
    """
    # Check if username already exists
    existing_user = await user_crud.get_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    user = await user_crud.create(
        db,
        obj_in={
            "username": username,
            "password": password,  # Note: Ensure password hashing is handled in crud
            "role_id": role_id
        }
    )
    
    return {"message": "User registered successfully", "user_id": user.id} 