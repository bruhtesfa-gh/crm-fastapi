from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import role_crud
from app.db import get_db
from app.deps import verify_access_token
from app.models import Role

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=List[Role])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
) -> List[Role]:
    """
    Get list of roles
    """
    return await role_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
) -> Role:
    """
    Get role by ID
    """
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=Role)
async def create_role(
    name: str,
    description: Optional[str] = None,
    permission_ids: Optional[List[int]] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
) -> Role:
    """
    Create new role
    """
    role = await role_crud.get_by_name(db, name=name)
    if role:
        raise HTTPException(status_code=400, detail="Role already exists")

    return await role_crud.create(
        db,
        obj_in={
            "name": name,
            "description": description,
            "permission_ids": permission_ids,
        },
    )


@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    permission_ids: Optional[List[int]] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
) -> Role:
    """
    Update role
    """
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    update_data: Dict[str, Any] = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description
    if permission_ids is not None:
        update_data["permission_ids"] = permission_ids

    return await role_crud.update(db, db_obj=role, obj_in=update_data)


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
):
    """
    Delete role
    """
    role = await role_crud.remove(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}


@router.post("/{role_id}/permissions/{permission_id}")
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
):
    """
    Add a permission to a role
    """
    role = await role_crud.add_permission(
        db, role_id=role_id, permission_id=permission_id
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Permission added to role successfully"}


@router.delete("/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_access_token),
):
    """
    Remove a permission from a role
    """
    role = await role_crud.remove_permission(
        db, role_id=role_id, permission_id=permission_id
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Permission removed from role successfully"}
