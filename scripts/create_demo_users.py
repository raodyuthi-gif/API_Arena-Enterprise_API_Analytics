"""
Demo User Bootstrapper
=======================
Creates the first admin account directly against the database (there's
a chicken-and-egg problem otherwise: creating a user via the API
requires an existing admin token). Also creates one analyst and one
viewer account so all three dashboard roles can be demoed immediately.

Usage:
    cd backend
    python ../scripts/create_demo_users.py

Safe to re-run: existing emails are skipped rather than duplicated.
"""
import asyncio
import sys

sys.path.insert(0, ".")  # run from backend/ so `app` package resolves

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

DEMO_ACCOUNTS = [
    {
        "email": "admin@apiarena.dev",
        "username": "admin",
        "full_name": "Ava Administrator",
        "password": "Admin@12345",
        "role": UserRole.ADMIN,
    },
    {
        "email": "analyst@apiarena.dev",
        "username": "analyst",
        "full_name": "Alex Analyst",
        "password": "Analyst@12345",
        "role": UserRole.ANALYST,
    },
    {
        "email": "viewer@apiarena.dev",
        "username": "viewer",
        "full_name": "Vic Viewer",
        "password": "Viewer@12345",
        "role": UserRole.VIEWER,
    },
]


async def main():
    async with AsyncSessionLocal() as db:
        for account in DEMO_ACCOUNTS:
            existing = await db.execute(select(User).where(User.email == account["email"]))
            if existing.scalar_one_or_none():
                print(f"  · {account['email']} already exists — skipping")
                continue

            user = User(
                email=account["email"],
                username=account["username"],
                full_name=account["full_name"],
                hashed_password=AuthService.hash_password(account["password"]),
                role=account["role"],
                is_active=True,
            )
            db.add(user)
            print(f"  + created {account['role'].value:8s} {account['email']} / {account['password']}")

        await db.commit()

    print("\nDone. Sign in at the frontend login page with any of the accounts above.")


if __name__ == "__main__":
    asyncio.run(main())