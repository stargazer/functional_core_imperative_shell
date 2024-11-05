from collections.abc import AsyncGenerator
from typing import Any, AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .schema import Base


async_db_engine = create_async_engine("postgresql+asyncpg://username:password@postgres:5432/db")
async_db_session = async_sessionmaker(autocommit=False, autoflush=False, bind=async_db_engine)


async def init_models() -> None:
    """
    Creates the DB tables, if they don't exist
    """

    async with async_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db_session() -> AsyncIterator[AsyncSession]:
    """
    Yields an async DB session, that can be further injected as dependency in the API routes.
    
    Sessions will be request-scoped, meaning we don't need to handle transactions anywhere else; 
    If a route logic completes successfully, `session.commit()` executes and commits to the DB. If
    an exception occurs, the context manager rolls back the transaction.
    """

    async with async_db_session() as session:
        yield session
        await session.commit()