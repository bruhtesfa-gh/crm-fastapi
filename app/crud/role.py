from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Permission, Role


class CRUDRole:
    async def get(self, db: AsyncSession, id: int) -> Optional[Role]:
        """
        Get a role by ID, including its permissions
        """
        query = (
            select(Role).options(selectinload(Role.permissions)).where(Role.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        """
        Get a role by name
        """
        query = (
            select(Role)
            .where(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Role]:
        """
        Get multiple roles with pagination
        """
        query = (
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> Role:
        """
        Create new role
        """
        db_obj = Role(name=obj_in["name"], description=obj_in.get("description"))

        # Handle permissions if provided
        if "permission_ids" in obj_in:
            permissions = await self._get_permissions(db, obj_in["permission_ids"])
            db_obj.permissions = permissions

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Role, obj_in: Union[Dict[str, Any], Any]
    ) -> Role:
        """
        Update role
        """
        update_data = obj_in.copy() if isinstance(obj_in, dict) else obj_in.dict()

        # Handle permissions separately
        permission_ids = update_data.pop("permission_ids", None)

        # Update basic fields
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Update permissions if provided
        if permission_ids is not None:
            permissions = await self._get_permissions(db, permission_ids)
            db_obj.permissions = permissions

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Role]:
        """
        Delete role
        """
        obj = await self.get(db, id=id)
        if obj:
            # Remove all permission associations
            obj.permissions = []
            await db.delete(obj)
            await db.commit()
        return obj

    async def add_permission(
        self, db: AsyncSession, *, role_id: int, permission_id: int
    ) -> Optional[Role]:
        """
        Add a permission to a role
        """
        role = await self.get(db, id=role_id)
        if not role:
            return None

        permission = await self._get_permission(db, permission_id)
        if permission and permission not in role.permissions:
            role.permissions.append(permission)
            await db.commit()
            await db.refresh(role)

        return role

    async def remove_permission(
        self, db: AsyncSession, *, role_id: int, permission_id: int
    ) -> Optional[Role]:
        """
        Remove a permission from a role
        """
        role = await self.get(db, id=role_id)
        if not role:
            return None

        permission = await self._get_permission(db, permission_id)
        if permission and permission in role.permissions:
            role.permissions.remove(permission)
            await db.commit()
            await db.refresh(role)

        return role

    async def _get_permission(
        self, db: AsyncSession, permission_id: int
    ) -> Optional[Permission]:
        """
        Helper method to get a permission by ID
        """
        query = select(Permission).where(Permission.id == permission_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _get_permissions(
        self, db: AsyncSession, permission_ids: List[int]
    ) -> List[Permission]:
        """
        Helper method to get multiple permissions by IDs
        """
        query = select(Permission).where(Permission.id.in_(permission_ids))
        result = await db.execute(query)
        return result.scalars().all()


# Create a singleton instance
role_crud = CRUDRole()
