from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator


DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eurobound"

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0 declarative base with strict typing integration."""

    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional async session scope for API operations.
    """
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
