from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.audit import crud_audit
from app.models import EntityType, Permission, Role
from app.schema.auditlog import AuditLogCreate
from app.schema.user import RoleCreate, RoleUpdate


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

    async def create(
        self, db: AsyncSession, *, obj_in: RoleCreate, user_id: int
    ) -> Role:
        """
        Create new role
        """
        db_obj = Role(name=obj_in.name, description=obj_in.description)

        # Handle permissions if provided
        if obj_in.permissions:
            permissions = await self._get_permissions(db, obj_in.permissions)
            db_obj.permissions = permissions

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        after_values = jsonable_encoder(db_obj)
        _obj_in = AuditLogCreate(
            entity_type=EntityType.ROLE,
            entity_id=db_obj.id,
            user_id=user_id,
            action="Create Role",
            after_values=after_values,
        )
        crud_audit.create(db, obj_in=_obj_in)
        role = await self.get(db, db_obj.id)
        return role if role else db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Role, obj_in: RoleUpdate, user_id: int
    ) -> Role:
        """
        Update role
        """
        before_values = jsonable_encoder(db_obj)
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
        if permission_ids is not None:
            before_values = jsonable_encoder(db_obj.permissions)
            action = "Update Role Permissions"
            after_values = jsonable_encoder(permissions)
        else:
            action = "Update Role"
            after_values = jsonable_encoder(db_obj)
        _obj_in = AuditLogCreate(
            entity_type=EntityType.ROLE,
            entity_id=db_obj.id,
            user_id=user_id,
            action=action,
            before_values=before_values,
            after_values=after_values,
        )
        crud_audit.create(db, obj_in=_obj_in)
        return db_obj

    async def remove(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> Optional[Role]:
        """
        Delete role
        """
        obj = await self.get(db, id=id)
        if obj:
            # Remove all permission associations
            obj.permissions = []
            await db.delete(obj)
            await db.commit()
            before_values = jsonable_encoder(obj)
            _obj_in = AuditLogCreate(
                entity_type=EntityType.ROLE,
                entity_id=obj.id,
                user_id=user_id,
                action="Delete Role",
                before_values=before_values,
            )
            crud_audit.create(db, obj_in=_obj_in)
        return obj

    async def add_permission(
        self, db: AsyncSession, *, role_id: int, permission_id: int, user_id: int
    ) -> Optional[Role]:
        """
        Add a permission to a role
        """
        role = await self.get(db, id=role_id)
        if not role:
            return None
        before_values = jsonable_encoder(role.permissions)
        permission = await self._get_permission(db, permission_id)
        if permission and permission not in role.permissions:
            role.permissions.append(permission)
            await db.commit()
            await db.refresh(role)
            after_values = jsonable_encoder(role.permissions)
            _obj_in = AuditLogCreate(
                entity_type=EntityType.ROLE,
                entity_id=role.id,
                user_id=user_id,
                action="Add Permission to Role",
                before_values=before_values,
                after_values=after_values,
            )
            crud_audit.create(db, obj_in=_obj_in)
        return role

    async def remove_permission(
        self, db: AsyncSession, *, role_id: int, permission_id: int, user_id: int
    ) -> Optional[Role]:
        """
        Remove a permission from a role
        """
        role = await self.get(db, id=role_id)
        if not role:
            return None
        before_values = jsonable_encoder(role.permissions)
        permission = await self._get_permission(db, permission_id)
        if permission and permission in role.permissions:
            role.permissions.remove(permission)
            await db.commit()
            await db.refresh(role)
            after_values = jsonable_encoder(role.permissions)
            _obj_in = AuditLogCreate(
                entity_type=EntityType.ROLE,
                entity_id=role.id,
                user_id=user_id,
                action="Remove Permission from Role",
                before_values=before_values,
                after_values=after_values,
            )
            crud_audit.create(db, obj_in=_obj_in)
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
