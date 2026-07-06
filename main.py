"""
PawPal+ — main.py demo

Adds tasks out of order (mixed preferred_time values, some missing),
then proves out Scheduler.sort_by_time() and Scheduler.filter_tasks()
by printing the results to the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_tasks(label, tasks):
    print(f"\n{label}")
    print("-" * len(label))
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        print(f"  {t}")


def main():
    owner = Owner("Jamie", available_start="07:00", available_end="21:00")

    rex = Pet("Rex", "dog", breed="Labrador")
    milo = Pet("Milo", "cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # --- Add tasks deliberately OUT OF ORDER by time ---
    rex.add_task(Task("Evening walk", 30, priority="high", preferred_time="18:00"))
    rex.add_task(Task("Breakfast", 10, priority="critical", preferred_time="07:30", frequency="daily"))
    rex.add_task(Task("Fetch in the yard", 20, priority="low"))  # no preferred_time
    rex.add_task(Task("Midday potty break", 10, priority="medium", preferred_time="12:30"))

    milo.add_task(Task("Litter box scoop", 5, priority="medium", preferred_time="09:00", frequency="daily"))
    milo.add_task(Task("Evening feeding", 10, priority="high", preferred_time="19:00"))
    milo.add_task(Task("Brushing", 15, priority="low", preferred_time="08:00", frequency="weekly"))

    # Mark a couple of tasks complete to exercise the status filter
    rex.tasks[1].mark_complete()   # Breakfast
    milo.tasks[2].mark_complete()  # Brushing

    scheduler = Scheduler(owner, rex)

    # --- Sorting demo ---
    all_tasks_unsorted = [task for pet in owner.pets for task in pet.tasks]
    print_tasks("All tasks, in the order they were added (out of order)", all_tasks_unsorted)

    sorted_tasks = scheduler.sort_by_time()
    print_tasks("All tasks, sorted chronologically by preferred_time", sorted_tasks)

    # --- Filtering demo ---
    incomplete = scheduler.filter_tasks(completed=False)
    print_tasks("Incomplete tasks (all pets)", incomplete)

    completed = scheduler.filter_tasks(completed=True)
    print_tasks("Completed tasks (all pets)", completed)

    rex_only = scheduler.filter_tasks(pet_name="Rex")
    print_tasks("Rex's tasks only", rex_only)

    milo_incomplete = scheduler.filter_tasks(completed=False, pet_name="Milo")
    print_tasks("Milo's incomplete tasks only", milo_incomplete)

    # --- Recurring task auto-renewal demo ---
    print_tasks("Rex's tasks BEFORE completing the daily 'Fetch in the yard'", rex.tasks)

    # Make "Fetch in the yard" a daily task so we can prove out recurrence,
    # then complete it via the household-wide Scheduler method.
    fetch_task = rex.tasks[2]
    fetch_task.frequency = "daily"
    scheduler.mark_task_complete(fetch_task.id)

    print_tasks("Rex's tasks AFTER completing it (a fresh occurrence should appear)", rex.tasks)

    # Same idea for Milo's daily litter box scoop.
    print_tasks("Milo's tasks BEFORE completing the daily litter box scoop", milo.tasks)
    scheduler.mark_task_complete(milo.tasks[0].id)
    print_tasks("Milo's tasks AFTER completing it", milo.tasks)

    # --- Existing plan generation, unaffected by the new methods ---
    plan = scheduler.generate_plan()
    print("\nGenerated plan for Rex")
    print("-----------------------")
    for entry in plan["log"]:
        print(f"  {entry}")

    # --- Conflict detection demo ---
    # Two tasks at the exact same time, same pet:
    rex.add_task(Task("Vet call", 15, priority="medium", preferred_time="12:30"))
    # (Rex already has "Midday potty break" at 12:30 -- same-pet conflict)

    # Two tasks at the exact same time, different pets:
    milo.add_task(Task("Vet appointment prep", 10, priority="high", preferred_time="18:00"))
    # (Rex already has "Evening walk" at 18:00 -- cross-pet conflict)

    print_tasks("Rex's tasks after adding a same-time conflict", rex.tasks)
    print_tasks("Milo's tasks after adding a cross-pet conflict", milo.tasks)

    conflicts = scheduler.detect_conflicts()
    print("\nConflict check")
    print("--------------")
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")


if __name__ == "__main__":
    main()