from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models import TaskModel
from core.operations import TaskCore
from shell.common.deserializers import TaskCreateDeserializer
from shell.common.serializers import TaskSerializer
from shell.db.schema import Base, Task
from shell.db.sync_session import get_sync_db_session, init_models


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """
    Create the DB tables as soon as the server starts
    """
    
    init_models()
    yield


app = FastAPI(title="Synchronous Task API - Functional Core Example", lifespan=lifespan)


@app.get("/tasks", response_model=List[TaskSerializer])
def list_tasks(session: Session = Depends(get_sync_db_session)):

    # Retrieve all `Task` instances from the DB
    statement = select(Task)
    result = session.execute(statement)
    tasks = result.scalars().all()

    # Serialize and return
    return [TaskSerializer.model_validate(task) for task in tasks]


@app.post('/tasks', response_model=TaskSerializer)
def create_task(task: TaskCreateDeserializer, session: Session= Depends(get_sync_db_session)):

    # Create a `TaskModel` instance
    task_model = TaskCore.create(task.name)

    # Create a corresponding `Task` instance and commit to DB
    task = Task(**task_model.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)

    # Serialize and return
    return TaskSerializer.model_validate(task)


@app.put("/tasks/{task_id}/complete", response_model=TaskSerializer)
def complete_task(task_id: int, session: Session = Depends(get_sync_db_session)):

    # Retrieve the `Task instance from the DB`
    task = session.get(Task, task_id)

    # Convert it to a `TaskModel` instance
    task_model = TaskModel.model_validate(task)
    # Apply the `complete` function on the instance
    completed_task_model = TaskCore.complete(task_model)

    # Update the `Task` object accordingly
    for key, value in completed_task_model.model_dump().items():
        setattr(task, key, value)

    # Commit to DB
    session.commit()
    session.refresh(task)

    # Serialize and return
    return TaskSerializer.model_validate(task)