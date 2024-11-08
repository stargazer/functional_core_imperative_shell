import pytest
from typing import AsyncGenerator, Iterator, Generator

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from shell.sync_api.app import app, get_sync_db_session
from core.operations import TaskCore
from shell.db.schema import Base, Task


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
testdb_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SyncTestSessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=testdb_engine,
)


@pytest.fixture
def testdb_session() -> Iterator[Session]:
    """
    Returns a generator to `Session` objects.

    This function overrides the original `get_sync_db_session` function, and
    will be the dependency that gets injected into the API request handlers.
    """

    def _session() -> Iterator[Session]:

        with SyncTestSessionFactory() as session:
            try:
                yield session
                session.commit()
            finally:
                session.close()
   

    return _session

    #def _session():
    #    session = async_testdb_session()
    #    yield session
    #    session.close()

    #yield _session


@pytest.fixture
def cleanup_db() -> None:
    """
    Drops and recreates the database
    """

    Base.metadata.drop_all(bind=testdb_engine)
    Base.metadata.create_all(testdb_engine)


@pytest.fixture
def app_deps(testdb_session) -> None:
    """
    Overrides the API dependency `get_async_db_session` with the
    `testdb_session` function we defined earlier.
    """

    app.dependency_overrides[get_sync_db_session] = testdb_session


# Defines the API client. This client object overrides its `get_async_db_session` dependency
# to make use of the function defined above
@pytest.fixture
def client():
    """
    Returns the `TestClient` instance, bound to our FastAPI instance.
    """

    return TestClient(app)

@pytest.fixture
def test_data(cleanup_db, testdb_session):

    session_generator = testdb_session()
    session = next(session_generator)

    task_model = TaskCore.create('test_task')
    task = Task(**task_model.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)


# Tests
def test_get_tasks(client, app_deps, test_data):

    # session_generator = testdb_session()
    # session = next(session_generator)

    # task_model = TaskCore.create('test_task')
    # task = Task(**task_model.model_dump())
    # session.add(task)
    # session.commit()
    # session.refresh(task)

    # print(task.id)
    #  assert task.id is not None

    res = client.get('/tasks')
    print(res.content)
    assert res.status_code == 200