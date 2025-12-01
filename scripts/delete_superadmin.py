import asyncio
import os
import sys

from sqlalchemy import delete, select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.models import User, UserRole
from db.session import get_session


async def prompt_for_superadmin_credentials():
    username = input("Enter username of superadmin: ")

    async for session in get_session():
        await delete_superadmin(username, session)


async def delete_superadmin(username, session):
    """Delete a superadmin in the database"""
    async with session.begin():
        exists = await session.execute(select(User).where(User.username == username))
        user = exists.unique().scalar_one_or_none()

        if not user:
            print("Error: A user with this username does not exist.")
            return

        query_to_delete_user = delete(User).where(User.username == username)
        query_to_delete_role_relation = delete(UserRole).where(
            UserRole.user_id == user.id
        )

        try:
            await session.execute(query_to_delete_role_relation)
            await session.execute(query_to_delete_user)
            await session.commit()
            print(f"Superadmin {username} was deleted successfully!")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(prompt_for_superadmin_credentials())
