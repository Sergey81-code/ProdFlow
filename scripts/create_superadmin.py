import asyncio
import os
import re
import sys
from getpass import getpass

from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from uuid import uuid4

from api.core.config import get_settings
from config.permissions import Permissions
from db.models import Role, User, UserRole
from db.session import get_session

settings = get_settings()


def get_password(message):
    return getpass(message).strip()


async def is_free_username(username: str, session) -> bool:
    result = await session.execute(select(User).where(User.username == username))
    user = result.unique().scalars().first()
    return user is None


async def check_creation_super_role(super_role_name: str, session):
    result = await session.execute(select(Role).where(Role.name == super_role_name))
    role = result.scalars().first()
    return role.id if role is not None else None


def is_valid_password(password: str) -> bool:
    """Checks if the password meets security requirements."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


async def prompt_for_superadmin_credentials():
    async for session in get_session():
        while True:
            username = input("Enter username: ").strip()
            if username.lower() == "exit" or username == "exit()":
                print("Exiting...")
                sys.exit(0)
            if await is_free_username(username, session):
                break
            print("This username is already used.")

        while True:
            password = get_password("Enter password: ")
            if password.lower() == "exit" or password == "exit()":
                print("Exiting...")
                sys.exit(0)
            if is_valid_password(password):
                break
            print(
                "Password must be at least 8 characters long and contain uppercase and lowercase letters, numbers, and special characters. Type 'exit' or 'exit()' to exit the program."
            )

        while True:
            password2 = get_password("Repeat password: ")
            if password.lower() == "exit" or password == "exit()":
                print("Exiting...")
                sys.exit(0)
            if password2 == password:
                break
            print("Passwords do not match")

        name = input("Enter name (default: 'Admin'): ").strip() or "Admin"
        surname = input("Enter surname (default: 'Super'): ").strip() or "Super"

        await create_superadmin(username, password, name, surname, session)


async def create_superadmin(username, password, name, surname, session):
    """Create a superadmin in the database"""
    async with session.begin():
        super_role_id_or_none = await check_creation_super_role(
            settings.SUPER_ROLE_NAME, session
        )
        if super_role_id_or_none is None:
            new_super_role = Role(
                id=uuid4(),
                name=settings.SUPER_ROLE_NAME,
                permissions=[permission for permission in Permissions],
            )
            try:
                session.add(new_super_role)
                await session.flush()
                super_role_id_or_none = new_super_role.id
            except Exception as e:
                print(f"Unexpected error: {e}")

        new_superuser = User(
            id=uuid4(),
            username=username,
            first_name=name,
            last_name=surname,
            password=password,
        )

        new_role_of_user = UserRole(
            role_id=super_role_id_or_none, user_id=new_superuser.id
        )

        try:
            session.add(new_superuser)
            session.add(new_role_of_user)
            print(f"Superadmin {username} was created successfully!")
        except TypeError:
            print("Error: possibly an incorrect argument name in the User model.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(prompt_for_superadmin_credentials())
    except KeyboardInterrupt:
        print("Bye!")
