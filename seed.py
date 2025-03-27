# seed.py
import asyncio
from sqlalchemy import select
from app.models import Permission, Role, User  # Adjust these imports based on your project structure
from app.db import get_db, engine
from app.util.auth.hasher import hash_password

async def create_defaults():
    # Retrieve one session instance from the get_db generator
    async for session in get_db():
        # Check if default permissions already exist
        result = await session.execute(select(Permission))
        if result.scalars().first() is not None:
            print("Default permissions already exist. Skipping seeding.")
            return

        create_leads_permission = Permission(
            name="POST:/leads/create",
            description="Permission to create leads."
        )
        update_leads_permission = Permission(
            name="PUT:/leads/update",
            description="Permission to update leads."
        )

        view_leads_permission = Permission(
            name="GET:/leads",
            description="Permission to view leads."
        )

        draft_quotations_permission = Permission(
            name="POST:/quotations/draft",
            description="Permission to draft quotations."
        )

        update_quotations_permission = Permission(
            name="PUT:/quotations/update",
            description="Permission to update quotations."
        )

        approve_quotations_permission = Permission(
            name="PUT:/quotations/approve",
            description="Permission to approve or reject quotations."
        )

        view_quotations_permission = Permission(
            name="GET:/quotations",
            description="Permission to view quotations."
        )

        create_users_permission = Permission(
            name="POST:/users/create",
            description="Permission to create users."
        )

        update_users_permission = Permission(
            name="PUT:/users/update",
            description="Permission to update users."
        )
        
        update_users_role_permission = Permission(
            name="PUT:/users/role",
            description="Permission to update users role."
        )

        view_users_permission = Permission(
            name="GET:/users",
            description="Permission to view users."
        )

        view_users_role_permission = Permission(
            name="GET:/users/role",
            description="Permission to view users role."
        )

        view_audit_logs_permission = Permission(
            name="GET:/audit-logs",
            description="Permission to view audit logs."
        )
        
        
        # Create roles and assign permissions
        role_admin = Role(
            name="Admin",
            description="Administrator with full permissions."
        )

        # role admin have a permission to manage users
        role_admin.permissions = [create_users_permission, update_users_permission, update_users_role_permission, view_users_permission, view_users_role_permission]
        role_manager = Role(
            name="Manager",
            description="Manager with permission to approve quotations."
        )
        # role manager have a permission to approve quotations
        role_manager.permissions = [approve_quotations_permission]

        role_seals = Role(
            name="Sales Rep",
            description="Seals with permission to manage seals."
        )

        # role seals have a permission to create leads
        role_seals.permissions = [create_leads_permission, update_leads_permission, view_leads_permission, draft_quotations_permission, update_quotations_permission, view_quotations_permission]

        role_all = Role(
            name="All roles",
            description="All with permission to manage all."
        )
        role_all.permissions = [view_audit_logs_permission]


        # Create a default user assigned to the Admin role
        default_user = User(
            username="admin",
            hashed_password=hash_password("admin123"),  # Replace with secure password hashing
            role=role_admin
        )

        # Add all entities to the session and commit the changes
        session.add_all([
            create_leads_permission, update_leads_permission, view_leads_permission,
            draft_quotations_permission, update_quotations_permission, approve_quotations_permission,
            view_quotations_permission, create_users_permission, update_users_permission,
            update_users_role_permission, view_users_permission, view_users_role_permission,
            view_audit_logs_permission,
            role_admin, role_manager, role_seals, role_all, default_user
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
