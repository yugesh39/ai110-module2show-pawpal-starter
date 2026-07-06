"""
PawPal+ — Sample Data (seed_data.py)

Quick sandbox to tinker with the project: one owner, two pets, a handful
of tasks each. Run this file directly to see a generated plan printed out.
"""

from main import Owner, Pet, Task, Scheduler


def build_sample_owner() -> Owner:
    # --- Owner ---
    owner = Owner(name="Jordan", available_start="07:00", available_end="19:00")

    # --- Pet 1: Biscuit the dog ---
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever")
    biscuit.add_task(Task("Morning walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="07:30"))
    biscuit.add_task(Task("Breakfast feeding", duration_minutes=10, priority="critical", frequency="daily"))
    biscuit.add_task(Task("Evening walk", duration_minutes=30, priority="high", frequency="daily"))
    biscuit.add_task(Task("Brushing", duration_minutes=15, priority="low", frequency="weekly"))
    biscuit.add_task(Task("Give heartworm medication", duration_minutes=5, priority="critical", frequency="weekly"))

    # --- Pet 2: Whiskers the cat ---
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby")
    whiskers.add_task(Task("Litter box cleaning", duration_minutes=10, priority="high", frequency="daily"))
    whiskers.add_task(Task("Wet food feeding", duration_minutes=5, priority="critical", frequency="daily"))
    whiskers.add_task(Task("Play with feather toy", duration_minutes=15, priority="medium", frequency="daily"))
    whiskers.add_task(Task("Nail trim", duration_minutes=10, priority="low", frequency="weekly"))

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    return owner


def print_plan(owner: Owner) -> None:
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print(f"\nDaily plan for {owner.name}'s pets ({owner.available_start}–{owner.available_end}):\n")
    for entry in plan["schedule"]:
        pet = entry["task"]
        print(f"  {entry['start']}–{entry['end']}  [{entry['pet'].name}] {entry['task'].description} "
              f"(priority: {entry['task'].priority})")

    if plan["skipped"]:
        print("\nSkipped (ran out of time):")
        for pet, task in plan["skipped"]:
            print(f"  [{pet.name}] {task.description}")

    print("\nReasoning log:")
    for line in plan["log"]:
        print(f"  - {line}")


if __name__ == "__main__":
    sample_owner = build_sample_owner()
    print_plan(sample_owner)