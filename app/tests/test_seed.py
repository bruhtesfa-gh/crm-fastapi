# seed.py
import asyncio
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from app.models import Base, Permission, Role, User  # Adjust these imports based on your project structure
from app.tests.utils.db import get_test_db, engine
from app.util.auth.hasher import hash_password


async def create_defaults():
    print("Creating defaults")
    # Retrieve one session instance from the get_db generator
    async for session in get_test_db():  
        # Check if default permissions already exist
        result = await session.execute(select(Permission))
        if result.scalars().first() is not None:
            print("Default permissions already exist. Skipping seeding.")
            return
        permissions = [
          "POST:/auth/register/",
          "GET:/users/me/",
          "GET:/users/",
          "GET:/users/*/",
          "PUT:/users/*/",
          "DELETE:/users/*/",
          "PUT:/users/*/role/",
          "GET:/roles/",
          "POST:/roles/",
          "GET:/roles/*/",
          "PUT:/roles/*/",
          "DELETE:/roles/*/",
          "POST:/roles/*/permissions/*/",
          "DELETE:/roles/*/permissions/*/",
          "GET:/leads/",
          "POST:/leads/",
          "GET:/leads/*/",
          "PUT:/leads/*/",
          "DELETE:/leads/*/",
          "PUT:/leads/*/status/",
          "GET:/quotations/",
          "POST:/quotations/",
          "GET:/quotations/*/",
          "DELETE:/quotations/*/",
          "PUT:/quotations/*/line-items/",
          "PUT:/quotations/*/status/",
          "POST:/quotations/*/send/",
          "GET:/audit-logs/",
          "GET:/audit-logs/*/"
        ]
        for permission in permissions:
            permission = Permission(
                name=permission,
                description="Permission to " + permission
            )
            session.add(permission)
        
        await session.commit()
        
        admin_permissions = await session.execute(select(Permission).where(Permission.name.ilike(f"%users%") 
                                                                     | Permission.name.ilike(f"%roles%"))
                                                                    )
        admin_permissions = admin_permissions.scalars().all()
        print(jsonable_encoder(admin_permissions))
        manager_permissions = await session.execute(select(Permission).where(
            Permission.name.ilike(f"%leads%") 
            | Permission.name.ilike(f"%quotations%"))
            )
        manager_permissions = manager_permissions.scalars().all()
        seals_permissions = await session.execute(select(Permission).where(
            Permission.name.ilike(f"%leads%") 
                | Permission.name.ilike(f"%quotations%"))
            )
        seals_permissions = seals_permissions.scalars().all()
        all_permissions = await session.execute(select(Permission).where(
            Permission.name.ilike(f"%audit-logs%")
            )
            )
        all_permissions = all_permissions.scalars().all()

        role_admin = Role(
            name="Admin",
            description="Admin with permission to manage users, roles, and audit logs."
        )
        role_admin.permissions = admin_permissions

        # role admin have a permission to manage users
        role_manager = Role(
            name="Manager",
            description="Manager with permission to approve quotations."
        )


        # role manager have a permission to approve quotations
        role_manager.permissions = manager_permissions

        role_seals = Role(
            name="Sales Rep",
            description="Sales Rep with permission to manage leads and quotations."
        )

        # role seals have a permission to create leads
        role_seals.permissions = seals_permissions

        role_all = Role(
            name="All roles",
            description="All with permission to manage all."
        )
        role_all.permissions = all_permissions


        # Create a default user assigned to the Admin role
        admin_user = User(
            username="admin@gmail.com",
            hashed_password=hash_password("admin123"),  # Replace with secure password hashing
            role=role_admin
        )
        manager_user = User(
            username="manager@gmail.com",
            hashed_password=hash_password("manager123"),  # Replace with secure password hashing
            role=role_manager
        )

        seals_user = User(
            username="seals@gmail.com",
            hashed_password=hash_password("seals123"),  # Replace with secure password hashing
            role=role_seals
        )

        all_user = User(
            username="all@gmail.com",
            hashed_password=hash_password("all123"),  # Replace with secure password hashing
            role=role_all
        )
        
        # Add all entities to the session and commit the changes
        session.add_all([
            role_admin, role_manager, role_seals, role_all, admin_user, manager_user, seals_user, all_user
        ])
        await session.commit()
        print("Default permissions, roles, and user seeded successfully.")
        break  # Use only the first session obtained

async def create_tables():
    # Create all tables based on the metadata defined in your models.
    async with engine.begin() as conn:
        # Replace Permission.metadata with the metadata shared by your models if necessary.
        await conn.run_sync(lambda sync_conn: Permission.metadata.create_all(bind=sync_conn))

async def main():
    await create_tables()
    await create_defaults()

if __name__ == "__main__":
    asyncio.run(main())
