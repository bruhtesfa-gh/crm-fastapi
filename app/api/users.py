from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import role_crud, user_crud
from app.db import get_db
from app.deps import get_auth_user, get_role_user
from app.schema import MeUser, UpdateUserBody, UpdateUserRoleBody

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=MeUser)
async def get_current_user(
    db: AsyncSession = Depends(get_db), me: MeUser = Depends(get_auth_user)
) -> dict:
    """
    Get current user information
    """
    user = await user_crud.get(db, id=1)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/", response_model=List[MeUser])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    role_user: MeUser = Depends(get_role_user(["Admin"])),
) -> List[MeUser]:
    """
    Get list of users
    """
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return jsonable_encoder(users)


@router.get("/{user_id}", response_model=MeUser)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    me: MeUser = Depends(get_auth_user),
) -> dict:
    """
    Get user by ID
    """
    if user_id != me.id:
        Depends(get_role_user(["Manager"]))
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=MeUser)
async def update_user(
    user_id: int,
    body: UpdateUserBody,
    db: AsyncSession = Depends(get_db),
    me: MeUser = Depends(get_auth_user),
) -> dict:
    """
    Update user information
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id != me.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this user"
        )

    update_data = {}
    if body.username:
        update_data["username"] = body.username

    updated_user = await user_crud.update(db, db_obj=user, obj_in=update_data)
    return updated_user


@router.put("/{user_id}/role", response_model=MeUser)
async def update_user_role(
    user_id: int,
    body: UpdateUserRoleBody,
    db: AsyncSession = Depends(get_db),
    me: MeUser = Depends(get_role_user(["Admin"])),
) -> dict:
    """
    Update user role
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role_db = await role_crud.get_by_name(db, name=body.role)
    if not role_db:
        raise HTTPException(status_code=404, detail="Role not found")

    update_data = {"role_id": role_db.id}
    updated_user = await user_crud.update(db, db_obj=user, obj_in=update_data)
    return updated_user


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    me: MeUser = Depends(get_auth_user),
) -> dict:
    """
    Delete user
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != me.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this user"
        )

    await user_crud.remove(db, id=user_id)
    return {"message": "User deleted successfully"}
