from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings


class Base(DeclarativeBase):
    pass


# Async engine for FastAPI
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# Sync engine for tests and scripts
def get_sync_engine(url: str = "sqlite:///:memory:"):
    return create_engine(url)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
