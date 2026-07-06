"""
PawPal+ — Core Classes (models.py)

Four core classes:
    Task      — a single activity (description, time, frequency, completion status)
    Pet       — pet details + its list of tasks
    Owner     — manages multiple pets, gives access to all their tasks
    Scheduler — the "brain": retrieves, organizes, and manages tasks across pets
"""

import uuid
from datetime import datetime, timedelta


class Task:
    """Represents a single care activity for a pet."""

    PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    VALID_FREQUENCIES = {"once", "daily", "weekly"}

    def __init__(
        self,
        description: str,
        duration_minutes: int,
        priority: str = "medium",
        frequency: str = "daily",
        scheduled_time: str = None,
        completed: bool = False,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority if priority in self.PRIORITY_LEVELS else "medium"
        self.frequency = frequency if frequency in self.VALID_FREQUENCIES else "daily"
        self.scheduled_time = scheduled_time      # optional hint, e.g. "08:00"
        self.completed = completed

    def priority_value(self) -> int:
        """Return the numeric weight of this task's priority for sorting."""
        return self.PRIORITY_LEVELS.get(self.priority, 2)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def edit(self, **kwargs) -> None:
        """Update one or more fields on this task."""
        for key, value in kwargs.items():
            if key == "priority" and value not in self.PRIORITY_LEVELS:
                continue
            if key == "frequency" and value not in self.VALID_FREQUENCIES:
                continue
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.description} ({self.duration_minutes}min, {self.priority})"


class Pet:
    """Represents a single pet and the tasks associated with it."""

    def __init__(self, name: str, species: str, breed: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a new task to this pet's task list."""
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates) -> bool:
        """Find a task by id and update its fields. Return True if found."""
        for task in self.tasks:
            if task.id == task_id:
                task.edit(**updates)
                return True
        return False

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from this pet's task list by id. Return True if removed."""
        original_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        return len(self.tasks) != original_len

    def get_incomplete_tasks(self) -> list[Task]:
        """Return only the tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def __repr__(self) -> str:
        return f"Pet({self.name}, {self.species}, tasks={len(self.tasks)})"


class Owner:
    """Represents the pet owner. Manages multiple pets and their tasks."""

    def __init__(self, name: str, available_start: str = "07:00", available_end: str = "21:00"):
        self.name = name
        self.available_start = available_start   # e.g. "07:00"
        self.available_end = available_end       # e.g. "21:00"
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by id. Return True if removed."""
        original_len = len(self.pets)
        self.pets = [p for p in self.pets if p.id != pet_id]
        return len(self.pets) != original_len

    def get_pet(self, pet_id: str) -> Pet | None:
        """Look up a single pet by id."""
        for pet in self.pets:
            if pet.id == pet_id:
                return pet
        return None

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across every pet, paired with its owning pet."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet, task))
        return all_tasks

    def available_minutes(self) -> int:
        """Return total minutes available between available_start and available_end."""
        fmt = "%H:%M"
        start = datetime.strptime(self.available_start, fmt)
        end = datetime.strptime(self.available_end, fmt)
        return int((end - start).total_seconds() // 60)

    def __repr__(self) -> str:
        return f"Owner({self.name}, pets={len(self.pets)})"


class Scheduler:
    """
    The 'brain' of PawPal+. Retrieves, organizes, and manages tasks
    across ALL of an owner's pets to build a single daily plan.
    """

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> dict:
        """
        Build and return a daily plan spanning every pet the owner has.

        Returns:
        {
            "schedule": [
                {"pet": Pet, "task": Task, "start": "08:00", "end": "08:30"}, ...
            ],
            "skipped": [(Pet, Task), ...],
            "log": ["reasoning string", ...]
        }
        """
        all_tasks = self.owner.get_all_tasks()
        pending = [(pet, task) for pet, task in all_tasks if not task.completed]
        sorted_tasks = self._sort_tasks(pending)

        minutes_left = self.owner.available_minutes()
        current_time = self.owner.available_start

        schedule, skipped, log = [], [], []

        for pet, task in sorted_tasks:
            if task.duration_minutes <= minutes_left:
                start, end = self._allocate_time(current_time, task.duration_minutes)
                schedule.append({"pet": pet, "task": task, "start": start, "end": end})
                current_time = end
                minutes_left -= task.duration_minutes
                log.append(
                    f"Scheduled '{task.description}' for {pet.name} "
                    f"({task.priority}) at {start}"
                )
            else:
                skipped.append((pet, task))
                log.append(
                    f"Skipped '{task.description}' for {pet.name} — not enough time left"
                )

        return {"schedule": schedule, "skipped": skipped, "log": log}

    def _sort_tasks(self, pet_task_pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort (pet, task) pairs by priority (desc), then duration (asc)."""
        return sorted(
            pet_task_pairs,
            key=lambda pair: (-pair[1].priority_value(), pair[1].duration_minutes),
        )

    def _allocate_time(self, current_time: str, duration: int) -> tuple[str, str]:
        """Add duration minutes to current_time. Return (start, end) as 'HH:MM' strings."""
        fmt = "%H:%M"
        start_dt = datetime.strptime(current_time, fmt)
        end_dt = start_dt + timedelta(minutes=duration)
        return start_dt.strftime(fmt), end_dt.strftime(fmt)