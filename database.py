import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use the DATABASE_URL from environment variables, fallback to a default if not set
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/default_db"
)

# Create the SQLAlchemy async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the session factory
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Create the declarative base for defining models
Base = declarative_base()  # This is what your models will inherit from


# Dependency to get the database session
async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
