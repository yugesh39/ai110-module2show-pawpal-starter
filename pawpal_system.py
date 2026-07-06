"""
PawPal+ — Class Skeleton
Generated from the Mermaid UML diagram (pawpal_uml.mmd).

This file contains structural stubs only — no logic implemented yet.
Fill in method bodies incrementally per the suggested workflow.
"""

import uuid


class Owner:
    """Represents the pet owner and their daily availability."""

    def __init__(self, name: str, available_start: str, available_end: str):
        """Initialize an owner with a name and their daily availability window."""
        self.name = name
        self.available_start = available_start   # e.g. "07:00"
        self.available_end = available_end       # e.g. "21:00"
        self.pets: list["Pet"] = []

    def add_pet(self, pet: "Pet") -> None:
        """Add a pet to this owner's list of pets."""
        pass

    def available_minutes(self) -> int:
        """Return total minutes available between available_start and available_end."""
        pass


class Pet:
    """Represents a single pet and the tasks associated with it."""

    def __init__(self, name: str, species: str, breed: str = ""):
        """Initialize a pet with a name, species, optional breed, and an empty task list."""
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks: list["Task"] = []

    def add_task(self, task: "Task") -> None:
        """Add a new task to this pet's task list."""
        pass

    def edit_task(self, task_id: str, **updates) -> bool:
        """Find a task by id and update its fields. Return True if found."""
        pass

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet's task list by id."""
        pass


class Task:
    """Represents a single care task for a pet."""

    PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}

    def __init__(
        self,
        name: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "general",
        preferred_time: str = None,
    ):
        """Initialize a task with a unique id, name, duration, priority, category, and optional preferred time."""
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low" | "medium" | "high" | "critical"
        self.category = category          # walk, feeding, meds, grooming, enrichment
        self.preferred_time = preferred_time

    def priority_value(self) -> int:
        """Return the numeric weight of this task's priority for sorting."""
        pass

    def edit(self, **kwargs) -> None:
        """Update one or more fields on this task."""
        pass


class Scheduler:
    """Generates a daily plan for a pet based on an owner's availability."""

    def __init__(self, owner: "Owner", pet: "Pet"):
        """Initialize the scheduler with the owner and pet it will build a plan for."""
        self.owner = owner
        self.pet = pet

    def generate_plan(self) -> dict:
        """
        Build and return a daily plan.

        Expected return shape:
        {
            "schedule": [{"task": Task, "start": "08:00", "end": "08:30"}, ...],
            "skipped": [Task, ...],
            "log": ["reasoning string", ...]
        }
        """
        pass

    def _sort_tasks(self, tasks: list["Task"]) -> list["Task"]:
        """Sort tasks by priority (desc), then duration."""
        pass

    def _allocate_time(self, current_time: str, duration: int) -> tuple:
        """Add duration minutes to current_time. Return (start, end) as strings."""
        pass