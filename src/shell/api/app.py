from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from core.models import TaskModel
from core.operations import TaskCore
from shell.db.session import get_db, engine
from shell.db.schema import Base, Task
from .deserializers import TaskCreateDeserializer
from .serializers import TaskSerializer


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task API - Functional Core Example")


@app.get("/tasks/", response_model=List[TaskSerializer])
def list_tasks( db: Session = Depends(get_db)):

    # Retrieve all `Task` instances from the DB
    tasks = db.query(Task).all()    

    # Serialize and return
    return [TaskSerializer.model_validate(task) for task in tasks]

@app.post('/tasks', response_model=TaskSerializer)
def create_task(task: TaskCreateDeserializer, db: Session=Depends(get_db)):

    # Create a `TaskModel` instance
    task_model = TaskCore.create(task.name)

    # Create a corresponding `Task` instance and commit to DB
    task = Task(**task_model.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)

    # Serialize and return
    return TaskSerializer.model_validate(task)

@app.put("/tasks/{task_id}/complete", response_model=TaskSerializer)
def complete_task(task_id: int, db: Session = Depends(get_db)):

    # Retrieve the `Task instance from the DB`
    task = db.query(Task).get(task_id)
    # Convert it to a `TaskModel` instance
    task_model = TaskModel.model_validate(task)
    # Apply the `complete` function on the instance
    completed_task_model = TaskCore.complete(task_model)

    # Update the `Task` object accordingly
    for key, value in completed_task_model.model_dump().items():
        print(key, value)
        setattr(task, key, value)

    # Commit to DB
    db.commit()
    db.refresh(task)

    # Serialize and return
    return TaskSerializer.model_validate(task)