from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Role, User
from app.util.auth.hasher import hash_password, verify_password


class CRUDUser:
    async def get(self, db: AsyncSession, id: int) -> Optional[User]:
        """
        Get a user by ID
        """
        query = (
            select(User)
            .where(User.id == id)
            .options(selectinload(User.role).options(selectinload(Role.permissions)))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        Get a user by username
        """
        query = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.role).options(selectinload(Role.permissions)))
        )
        result = await db.execute(query)
        print(result)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get multiple users with pagination
        """
        query = (
            select(User)
            .options(selectinload(User.role).options(selectinload(Role.permissions)))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> User:
        """
        Create new user
        """
        db_obj = User(
            username=obj_in["username"],
            hashed_password=hash_password(obj_in["password"]),
            role_id=obj_in["role_id"],
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Re-query the user with joined eager loading to fetch role and permissions
        query = (
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[Dict[str, Any], Any]
    ) -> User:
        """
        Update user
        """
        update_data = obj_in.copy() if isinstance(obj_in, dict) else obj_in.dict()

        if "password" in update_data:
            hashed_password = hash_password(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[User]:
        """
        Delete user
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user
        """
        user = await self.get_by_username(db, username=username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        return user


# Create a singleton instance
user_crud = CRUDUser()
