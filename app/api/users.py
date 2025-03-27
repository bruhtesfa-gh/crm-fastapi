from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import User
from app.schema.index import MeUser
from app.crud import user as user_crud
from typing import List
from app.deps import get_auth_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_auth_user)
) -> dict:
    """
    Get current user information
    """
    user = await user_crud.get(db, id=user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[MeUser])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_auth_user)
) -> List[User]:
    """
    Get list of users
    """
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_auth_user)
) -> dict:
    """
    Get user by ID
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    username: str = None,
    role_id: int = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_auth_user)
) -> dict:
    """
    Update user information
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {}
    if username:
        update_data["username"] = username
    if role_id:
        update_data["role_id"] = role_id
    
    updated_user = await user_crud.update(db, db_obj=user, obj_in=update_data)
    return updated_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_auth_user)
) -> dict:
    """
    Delete user
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_crud.remove(db, id=user_id)
    return {"message": "User deleted successfully"} 