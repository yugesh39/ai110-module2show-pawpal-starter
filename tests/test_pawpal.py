"""
PawPal+ — test_pawpal_system.py

Test suite covering the core behaviors and edge cases identified in the
testing plan for a pet scheduler with sorting, filtering, recurrence,
and conflict detection.
"""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


def make_owner(start="07:00", end="21:00"):
    return Owner("Jamie", available_start=start, available_end=end)


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

class TestSortByTime:
    def test_empty_task_list(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        assert scheduler.sort_by_time() == []

    def test_all_none_preferred_time(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("A", 10))
        pet.add_task(Task("B", 10))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        result = scheduler.sort_by_time()
        assert len(result) == 2  # doesn't crash, doesn't drop tasks

    def test_none_times_sort_last(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("No time", 10))
        pet.add_task(Task("Morning", 10, preferred_time="08:00"))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        result = scheduler.sort_by_time()
        assert result[0].name == "Morning"
        assert result[1].name == "No time"

    def test_day_boundary_times(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Late", 10, preferred_time="23:59"))
        pet.add_task(Task("Early", 10, preferred_time="00:00"))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        result = scheduler.sort_by_time()
        assert [t.name for t in result] == ["Early", "Late"]

    def test_duplicate_times_are_stable(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("First", 10, preferred_time="08:00"))
        pet.add_task(Task("Second", 10, preferred_time="08:00"))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        result = scheduler.sort_by_time()
        # Python's sort is stable -- insertion order should be preserved for ties
        assert [t.name for t in result] == ["First", "Second"]


# ---------------------------------------------------------------------------
# Recurring tasks
# ---------------------------------------------------------------------------

class TestRecurringTasks:
    def test_once_task_does_not_recur(self):
        pet = Pet("Rex", "dog")
        task = Task("Vet visit", 30, frequency="once")
        pet.add_task(task)
        pet.mark_task_complete(task.id)
        assert len(pet.tasks) == 1
        assert pet.tasks[0].completed is True

    def test_daily_task_spawns_next_occurrence(self):
        pet = Pet("Rex", "dog")
        task = Task("Feed", 10, frequency="daily")
        pet.add_task(task)
        pet.mark_task_complete(task.id)
        assert len(pet.tasks) == 2
        original, new = pet.tasks
        assert original.completed is True
        assert new.completed is False
        assert new.id != original.id
        assert new.name == "Feed"

    def test_weekly_task_spawns_next_occurrence(self):
        pet = Pet("Rex", "dog")
        task = Task("Groom", 20, frequency="weekly")
        pet.add_task(task)
        pet.mark_task_complete(task.id)
        assert len(pet.tasks) == 2
        assert pet.tasks[1].frequency == "weekly"
        assert pet.tasks[1].completed is False

    def test_completing_daily_task_twice_does_not_double_spawn(self):
        """
        Completing the SAME task id twice (e.g. a duplicate button click)
        should not spawn a second occurrence, since the task is already
        completed the second time around.
        """
        pet = Pet("Rex", "dog")
        task = Task("Feed", 10, frequency="daily")
        pet.add_task(task)
        pet.mark_task_complete(task.id)
        assert len(pet.tasks) == 2

        # Complete the SAME original task id again
        pet.mark_task_complete(task.id)
        # BUG CHECK: mark_task_complete doesn't check task.completed before
        # spawning again, so calling it twice on the same id currently
        # spawns a second new occurrence rather than being a no-op.
        assert len(pet.tasks) == 2, (
            "Completing an already-completed task id should be a no-op, "
            "not spawn another occurrence."
        )

    def test_mark_task_complete_missing_id_returns_false(self):
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Feed", 10))
        assert pet.mark_task_complete("nonexistent") is False

    def test_mark_task_complete_on_empty_pet(self):
        pet = Pet("Rex", "dog")
        assert pet.mark_task_complete("anything") is False

    def test_scheduler_mark_task_complete_searches_all_pets(self):
        owner = make_owner()
        rex = Pet("Rex", "dog")
        milo = Pet("Milo", "cat")
        task = Task("Litter box", 5, frequency="daily")
        milo.add_task(task)
        owner.add_pet(rex)
        owner.add_pet(milo)
        scheduler = Scheduler(owner, rex)

        assert scheduler.mark_task_complete(task.id) is True
        assert len(milo.tasks) == 2  # original + new occurrence


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

class TestFilterTasks:
    def setup_owner(self):
        owner = make_owner()
        rex = Pet("Rex", "dog")
        milo = Pet("Milo", "cat")
        rex.add_task(Task("Walk", 30, completed=False))
        rex.add_task(Task("Feed", 10, completed=True))
        milo.add_task(Task("Brush", 15, completed=False))
        owner.add_pet(rex)
        owner.add_pet(milo)
        return owner, rex, milo

    def test_filter_no_args_returns_all(self):
        owner, rex, milo = self.setup_owner()
        scheduler = Scheduler(owner, rex)
        assert len(scheduler.filter_tasks()) == 3

    def test_filter_unmatched_pet_name_returns_empty(self):
        owner, rex, milo = self.setup_owner()
        scheduler = Scheduler(owner, rex)
        assert scheduler.filter_tasks(pet_name="Ghost") == []

    def test_filter_pet_name_case_insensitive(self):
        owner, rex, milo = self.setup_owner()
        scheduler = Scheduler(owner, rex)
        result = scheduler.filter_tasks(pet_name="rex")
        assert len(result) == 2

    def test_filter_completed_and_pet_name_combined(self):
        owner, rex, milo = self.setup_owner()
        scheduler = Scheduler(owner, rex)
        result = scheduler.filter_tasks(completed=True, pet_name="Rex")
        assert len(result) == 1
        assert result[0].name == "Feed"


# ---------------------------------------------------------------------------
# Scheduling / time budget
# ---------------------------------------------------------------------------

class TestGeneratePlan:
    def test_task_longer_than_available_window_is_skipped(self):
        owner = make_owner(start="07:00", end="07:30")  # 30-minute day
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Long walk", 45))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        plan = scheduler.generate_plan()
        assert plan["schedule"] == []
        assert len(plan["skipped"]) == 1

    def test_zero_duration_task_does_not_hang(self):
        owner = make_owner(start="07:00", end="07:10")
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Instant check", 0))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        # Should complete without an infinite loop / hang
        plan = scheduler.generate_plan()
        assert len(plan["schedule"]) == 1
        assert plan["schedule"][0]["start"] == plan["schedule"][0]["end"]

    def test_zero_minute_day_skips_everything(self):
        owner = make_owner(start="09:00", end="09:00")
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Feed", 5))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        plan = scheduler.generate_plan()
        assert plan["schedule"] == []
        assert len(plan["skipped"]) == 1

    def test_completed_tasks_excluded_from_plan(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Done already", 10, completed=True))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        plan = scheduler.generate_plan()
        assert plan["schedule"] == []
        assert plan["skipped"] == []


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestDetectConflicts:
    def test_completed_task_not_flagged(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("A", 10, preferred_time="08:00", completed=True))
        pet.add_task(Task("B", 10, preferred_time="08:00", completed=False))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        assert scheduler.detect_conflicts() == []

    def test_three_way_conflict_lists_all(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("A", 10, preferred_time="08:00"))
        pet.add_task(Task("B", 10, preferred_time="08:00"))
        pet.add_task(Task("C", 10, preferred_time="08:00"))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "A" in conflicts[0] and "B" in conflicts[0] and "C" in conflicts[0]

    def test_cross_pet_conflict_detected(self):
        owner = make_owner()
        rex = Pet("Rex", "dog")
        milo = Pet("Milo", "cat")
        rex.add_task(Task("Walk", 30, preferred_time="18:00"))
        milo.add_task(Task("Feed", 10, preferred_time="18:00"))
        owner.add_pet(rex)
        owner.add_pet(milo)
        scheduler = Scheduler(owner, rex)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1

    def test_no_preferred_time_not_flagged(self):
        owner = make_owner()
        pet = Pet("Rex", "dog")
        pet.add_task(Task("A", 10))
        pet.add_task(Task("B", 10))
        owner.add_pet(pet)
        scheduler = Scheduler(owner, pet)
        assert scheduler.detect_conflicts() == []