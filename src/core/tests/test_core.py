import pytest

from core.models import TaskModel
from core.operations import TaskCore


def test_create():

    task = TaskCore.create(name='task_name')

    assert isinstance(task, TaskModel)
    assert task.name == 'task_name'
    assert task.completed_at is None
    assert task.created_at is not None

def test_complete():
    
    incomplete_task = TaskCore.create('task_name')
    assert incomplete_task.completed_at is None

    complete_task = TaskCore.complete(incomplete_task)
    assert complete_task.completed_at is not None