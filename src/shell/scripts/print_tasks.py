from sqlalchemy.orm import Session

from core.models import TaskModel
from core.operations import TaskCore
from shell.db.schema import Base, Task
from shell.db.session import engine, get_db


# Create database tables
Base.metadata.create_all(bind=engine)      


def print_tasks():

    db = next(get_db())

    task_rows = db.query(Task).all()
    task_models = [TaskModel.model_validate(row) for row in task_rows]
    print(task_models)


if __name__ == '__main__':
    print_tasks()