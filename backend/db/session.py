import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

settings = get_settings()

async_engine = create_async_engine(
    settings.ASYNC_REAL_DATABASE_URL, future=True, echo=True
)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_session():
    async with async_session() as session:
        yield session
