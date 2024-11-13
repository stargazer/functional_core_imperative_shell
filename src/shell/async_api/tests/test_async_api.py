import json
import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Iterator, Generator, AsyncIterator

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from core.operations import TaskCore
from shell.async_api.app import app, get_async_db_session
from shell.db.schema import Base, Task


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///.test.db"
testdb_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
AsyncTestSessionFactory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=testdb_engine,
)


async def get_testdb_session_generator() -> AsyncGenerator[AsyncSession, None]:
    """
    Returns a generator to `AsyncSession` objects.

    This function will override the original async API's `get_async_db_session` function, and will be the dependency that gets injected into the API request handlers.
    """

    async with AsyncTestSessionFactory() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        await session.close()

   
@pytest_asyncio.fixture   
async def session() -> AsyncSession:
    """
    Returns an `AsyncSession` instance
    """

    return await anext(get_testdb_session_generator())


@pytest_asyncio.fixture
async def cleanup_db() -> None:
    """
    Drops and recreates the database
    """

    async with testdb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)



@pytest.fixture
def app_deps() -> None:
    """
    Overrides the API dependency `get_async_db_session` to make use of
    the `get_testdb_session_generator` function.
    """

    app.dependency_overrides[get_async_db_session] = get_testdb_session_generator


@pytest.fixture
def client():
    """
    Returns the `TestClient` instance, bound to our FastAPI instance.
    """

    return TestClient(app)


@pytest_asyncio.fixture
async def create_test_data(session):
    """
    Creates the test data
    """

    task_models = [TaskCore.create('new task') for i in range(10)]

    tasks = [Task(**task_model.model_dump()) for task_model in task_models]  
    session.add_all(tasks)
    await session.commit()

### Tests

@pytest.mark.asyncio 
async def test_get_tasks(client, app_deps, cleanup_db, create_test_data):
    res = client.get('/tasks')
    data = json.loads(res.content)

    assert res.status_code == 200
    assert len(data) == 10


@pytest.mark.asyncio 
async def test_create_task(client, app_deps, cleanup_db, session):

    res = client.post('/tasks', json={'name': 'whatever'})

    assert res.status_code == 200

    # Retrieve all `Task` instances from the DB
    statement = select(Task)
    result = await session.execute(statement)
    tasks = result.scalars().all()
    assert len(tasks) == 1
    
    await session.close()


@pytest.mark.asyncio
async def test_complete_task(client, app_deps, cleanup_db, session, create_test_data):

    task = await session.execute(select(Task))
    task = task.scalars().first()
    task_id = task.id
    assert task.completed_at is None

    res = client.put('/tasks/{task_id}/complete'.format(task_id=task_id))

    await session.refresh(task)
    assert task.completed_at is not None
    
    await session.close()