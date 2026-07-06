"""
PawPal+ — Class Implementation
Generated from the Mermaid UML diagram (pawpal_uml.mmd).

Phase 2: method bodies implemented.
Phase 3: sort_by_time() and filter_tasks() added to Scheduler,
         plus a `completed` flag on Task so completion-status filtering works.
"""

import uuid
from datetime import datetime, timedelta


TIME_FORMAT = "%H:%M"


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
        self.pets.append(pet)

    def available_minutes(self) -> int:
        """Return total minutes available between available_start and available_end."""
        start = datetime.strptime(self.available_start, TIME_FORMAT)
        end = datetime.strptime(self.available_end, TIME_FORMAT)
        return int((end - start).total_seconds() // 60)


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
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates) -> bool:
        """Find a task by id and update its fields. Return True if found."""
        for task in self.tasks:
            if task.id == task_id:
                task.edit(**updates)
                return True
        return False

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet's task list by id."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def mark_task_complete(self, task_id: str) -> bool:
        """
        Find a task by id and mark it complete. If the task is "daily" or
        "weekly", automatically create and append a fresh instance for the
        next occurrence, so recurring chores keep showing up in future plans.

        Return True if the task was found (regardless of whether a new
        occurrence was spawned), False otherwise.
        """
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                if task.frequency in ("daily", "weekly"):
                    self.add_task(task.next_occurrence())
                return True
        return False


class Task:
    """Represents a single care task for a pet."""

    PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    VALID_FREQUENCIES = {"once", "daily", "weekly"}

    def __init__(
        self,
        name: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "general",
        preferred_time: str = None,
        completed: bool = False,
        frequency: str = "once",
    ):
        """Initialize a task with a unique id, name, duration, priority, category, optional preferred time, completion status, and recurrence frequency."""
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low" | "medium" | "high" | "critical"
        self.category = category          # walk, feeding, meds, grooming, enrichment
        self.preferred_time = preferred_time
        self.completed = completed        # needed to filter by completion status
        self.frequency = frequency if frequency in self.VALID_FREQUENCIES else "once"

    def priority_value(self) -> int:
        """Return the numeric weight of this task's priority for sorting."""
        return self.PRIORITY_LEVELS.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def next_occurrence(self) -> "Task":
        """
        Build a fresh Task representing the next occurrence of a recurring
        task: same name, duration, priority, category, preferred_time, and
        frequency, but a brand-new id and completed=False.

        There's no calendar date tracked on Task, so "next occurrence" just
        means "an identical, not-yet-done copy" -- it's up to whatever
        schedules tasks (e.g. Scheduler) to only surface it on the
        appropriate day. This is meant to be called once a task is marked
        complete, not called directly by most callers.
        """
        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            preferred_time=self.preferred_time,
            completed=False,
            frequency=self.frequency,
        )

    def edit(self, **kwargs) -> None:
        """Update one or more fields on this task."""
        for key, value in kwargs.items():
            if key == "frequency" and value not in self.VALID_FREQUENCIES:
                continue
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        time_str = self.preferred_time or "--:--"
        freq_str = f", {self.frequency}" if self.frequency != "once" else ""
        return f"[{status}] {time_str}  {self.name} ({self.duration_minutes}min, {self.priority}{freq_str})"


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
            "conflicts": ["warning string", ...],
            "log": ["reasoning string", ...]
        }
        """
        schedule = []
        skipped = []
        log = []

        current_time = self.owner.available_start
        end_of_day = datetime.strptime(self.owner.available_end, TIME_FORMAT)

        incomplete_tasks = [t for t in self.pet.tasks if not t.completed]
        sorted_tasks = self._sort_tasks(incomplete_tasks)

        for task in sorted_tasks:
            start_dt = datetime.strptime(current_time, TIME_FORMAT)
            projected_end = start_dt + timedelta(minutes=task.duration_minutes)

            if projected_end > end_of_day:
                skipped.append(task)
                log.append(
                    f"Skipped '{task.name}': not enough time left before "
                    f"{self.owner.available_end}."
                )
                continue

            start, end = self._allocate_time(current_time, task.duration_minutes)
            schedule.append({"task": task, "start": start, "end": end})
            log.append(
                f"Scheduled '{task.name}' ({task.priority} priority) from {start} to {end}."
            )
            current_time = end

        conflicts = self.detect_conflicts()
        log.extend(conflicts)

        return {"schedule": schedule, "skipped": skipped, "conflicts": conflicts, "log": log}

    def _sort_tasks(self, tasks: list["Task"]) -> list["Task"]:
        """Sort tasks by priority (desc), then duration."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_value(), t.duration_minutes),
        )

    def _allocate_time(self, current_time: str, duration: int) -> tuple:
        """Add duration minutes to current_time. Return (start, end) as strings."""
        start_dt = datetime.strptime(current_time, TIME_FORMAT)
        end_dt = start_dt + timedelta(minutes=duration)
        return start_dt.strftime(TIME_FORMAT), end_dt.strftime(TIME_FORMAT)

    def detect_conflicts(self) -> list[str]:
        """
        Lightweight conflict check across every pet the owner has.

        Rather than doing full interval-overlap math (which would require
        every task to reliably carry both a start and an end time), this
        groups incomplete tasks by their exact preferred_time string and
        flags any group with more than one task in it -- same pet or
        different pets, doesn't matter. This catches the common real case
        (two things pinned to "08:00") cheaply and predictably.

        Never raises. If preferred_time is missing, that task is simply
        skipped rather than causing an error. Returns a list of warning
        strings; an empty list means no conflicts were found.
        """
        warnings = []
        by_time: dict[str, list[tuple["Pet", "Task"]]] = {}

        for pet in self.owner.pets:
            for task in pet.tasks:
                if not task.preferred_time or task.completed:
                    continue
                by_time.setdefault(task.preferred_time, []).append((pet, task))

        for time_str, entries in sorted(by_time.items()):
            if len(entries) > 1:
                names = ", ".join(f"{pet.name}'s '{task.name}'" for pet, task in entries)
                warnings.append(f"⚠ Conflict at {time_str}: {names} are all scheduled at the same time.")

        return warnings

    def sort_by_time(self, tasks: list["Task"] = None) -> list["Task"]:
        """
        Sort tasks by their preferred_time attribute, in 'HH:MM' format.

        Since 'HH:MM' strings are zero-padded, plain string comparison already
        sorts them chronologically -- no need to parse into datetime objects.
        A lambda is used as the sort key. Tasks with no preferred_time (None)
        are pushed to the end rather than crashing the comparison.

        If no task list is given, sorts every task belonging to every pet
        this scheduler's owner has (not just self.pet), so it's useful for
        a full-household view.
        """
        if tasks is None:
            tasks = [task for pet in self.owner.pets for task in pet.tasks]

        return sorted(
            tasks,
            key=lambda t: (t.preferred_time is None, t.preferred_time or ""),
        )

    def mark_task_complete(self, task_id: str) -> bool:
        """
        Household-wide version of Pet.mark_task_complete: searches every pet
        this scheduler's owner has, marks the matching task complete, and
        (via Pet.mark_task_complete) automatically spawns the next occurrence
        if the task is "daily" or "weekly".

        Return True if the task was found on any pet, False otherwise.
        """
        for pet in self.owner.pets:
            if pet.mark_task_complete(task_id):
                return True
        return False

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> list["Task"]:
        """
        Filter tasks across all of the owner's pets by completion status
        and/or pet name. Either argument left as None is ignored.

        Examples:
            scheduler.filter_tasks(completed=False)          # all incomplete tasks
            scheduler.filter_tasks(pet_name="Rex")            # all of Rex's tasks
            scheduler.filter_tasks(completed=True, pet_name="Milo")
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results