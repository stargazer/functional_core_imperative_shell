from datetime import datetime, timezone
from typing import List, Optional, Tuple

from core.models import TaskModel


class TaskCore:
    """
    Pure functional core with the business logic for the `TaskModel` concept.
    It defines the functions that allow the shell to interact with the model.
    """
    
    @staticmethod
    def create(name: str) -> TaskModel:
        
        return TaskModel(
            name=name,
            completed_at=None,
            created_at=datetime.now(timezone.utc)
        )
   
    @staticmethod
    def complete(task: TaskModel) -> TaskModel:

        task.completed_at = datetime.now(timezone.utc)
        return task