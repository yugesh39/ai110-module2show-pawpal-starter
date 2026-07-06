"""
PawPal+ — Tests

Two simple tests as requested:
1. Task Completion — mark_complete() actually changes the task's status.
2. Task Addition — adding a task to a Pet increases that pet's task count.

Run with:
    python -m pytest
"""

from main import Pet, Task


def test_task_completion():
    """Calling mark_complete() should flip the task's completed status to True."""
    task = Task("Morning walk", duration_minutes=30, priority="high")

    assert task.completed is False  # sanity check on default state

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet("Biscuit", species="Dog", breed="Golden Retriever")
    initial_count = len(pet.tasks)

    pet.add_task(Task("Feeding", duration_minutes=10, priority="critical"))

    assert len(pet.tasks) == initial_count + 1