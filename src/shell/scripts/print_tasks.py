from sqlalchemy.orm import Session

from core.models import TaskModel
from core.operations import TaskCore
from shell.db.schema import Base, Task
from shell.db.sync_session import get_sync_db_session, init_models


# Create database tables
init_models()


def print_tasks():

    session = next(get_sync_db_session())

    task_rows = session.query(Task).all()
    task_models = [TaskModel.model_validate(row) for row in task_rows]
    print(task_models)


if __name__ == '__main__':
    print_tasks()