import json
import pytest
from typing import AsyncGenerator, Iterator, Generator

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from core.operations import TaskCore
from shell.db.schema import Base, Task
from shell.sync_api.app import app, get_sync_db_session


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


def get_testdb_session_generator() -> Generator[Session, None, None]:
    """
    Returns a generator to `Session` objects.

    This function will override the original sync API's `get_sync_db_session` function and will be the dependency that gets injected into the API request handlers.
    """

    with SyncTestSessionFactory() as session:
        try:
            yield session
        except:
            session.rollback()
            raise


@pytest.fixture
def session() -> Session:
    """
    Returns a `Session` instance
    """

    return next(get_testdb_session_generator())


@pytest.fixture
def cleanup_db() -> None:
    """
    Drops and recreates the database
    """

    Base.metadata.drop_all(bind=testdb_engine)
    Base.metadata.create_all(bind=testdb_engine)        


@pytest.fixture
def app_deps() -> None:
    """
    Overrides the API dependency `get_sync_db_session` to make use of the `get_testdb_session_generator` function
    """

    app.dependency_overrides[get_sync_db_session] = get_testdb_session_generator


@pytest.fixture
def client():
    """
    Returns the `TestClient` instance, bound to our FastAPI instance.
    """

    return TestClient(app)


@pytest.fixture
def create_test_data(session: Session):
    """
    Creates the test data
    """

    task_models = [TaskCore.create('new task') for i in range(10)]

    tasks = [Task(**task_model.model_dump()) for task_model in task_models]  
    session.add_all(tasks)
    session.commit()

### Tests

def test_get_tasks(client: TestClient, app_deps: None, cleanup_db: None, create_test_data: None):

    res = client.get('/tasks')
    data = json.loads(res.content)

    assert res.status_code == 200
    assert len(data) == 10


def test_create_task(client: TestClient, app_deps: None, cleanup_db: None, session: Session):

    res = client.post('/tasks', json={'name': 'whatever'})

    assert res.status_code == 200

    # Retrieve all `Task` isntances from the DB
    statement = select(Task)
    result = session.execute(statement)
    tasks = result.scalars().all()
    assert len(tasks) == 1
    session.close()


def test_complete_task(client: TestClient, app_deps: None, cleanup_db: None, session: Session, create_test_data: None):

    task = session.execute(select(Task)).scalars().first()
    task_id = task.id
    assert task.completed_at is None

    res = client.put('/tasks/{task_id}/complete'.format(task_id=task_id))

    session.refresh(task)
    assert task.completed_at is not None