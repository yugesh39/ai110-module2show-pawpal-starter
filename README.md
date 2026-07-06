
# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Daily plan for Jordan's pets (07:00–19:00):

  07:00–07:05  [Biscuit] Give heartworm medication (priority: critical)
  07:05–07:10  [Whiskers] Wet food feeding (priority: critical)
  07:10–07:20  [Biscuit] Breakfast feeding (priority: critical)
  07:20–07:30  [Whiskers] Litter box cleaning (priority: high)
  07:30–08:00  [Biscuit] Morning walk (priority: high)
  08:00–08:30  [Biscuit] Evening walk (priority: high)
  08:30–08:45  [Whiskers] Play with feather toy (priority: medium)
  08:45–08:55  [Whiskers] Nail trim (priority: low)
  08:55–09:10  [Biscuit] Brushing (priority: low)

Reasoning log:
  - Scheduled 'Give heartworm medication' for Biscuit (critical) at 07:00
  - Scheduled 'Wet food feeding' for Whiskers (critical) at 07:05
  - Scheduled 'Breakfast feeding' for Biscuit (critical) at 07:10
  - Scheduled 'Litter box cleaning' for Whiskers (high) at 07:20
  - Scheduled 'Morning walk' for Biscuit (high) at 07:30
  - Scheduled 'Evening walk' for Biscuit (high) at 08:00
  - Scheduled 'Play with feather toy' for Whiskers (medium) at 08:30
  - Scheduled 'Nail trim' for Whiskers (low) at 08:45
  - Scheduled 'Brushing' for Biscuit (low) at 08:55
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

## 📐 Smarter Scheduling

These features were added on top of the base priority/duration scheduler to make PawPal+ handle a
real household's messier reality: tasks entered out of order, tasks that repeat, and tasks that
collide on the clock.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Time-based sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by `preferred_time` ("HH:MM"). Tasks with no `preferred_time` are pushed to the end instead of erroring. Defaults to sorting every pet's tasks, not just one. |
| Filtering | `Scheduler.filter_tasks()` | Filters tasks across all of the owner's pets by `completed` status and/or `pet_name`, independently or combined. |
| Conflict detection | `Scheduler.detect_conflicts()` | Lightweight check: groups incomplete tasks by exact `preferred_time` and returns a human-readable warning for any time with more than one task, whether same pet or different pets. Never raises — returns warnings instead of crashing. Automatically included in `Scheduler.generate_plan()`'s log. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()`, `Scheduler.mark_task_complete()` | Completing a `"daily"` or `"weekly"` task automatically spawns a fresh, incomplete copy of it for the next occurrence. `Pet.mark_task_complete()` does this for one pet; `Scheduler.mark_task_complete()` searches across every pet the owner has. `Scheduler.generate_plan()` excludes already-completed tasks so a finished task and its new copy don't both get scheduled. |

### Design notes

- **Sorting** uses a tuple sort key (`(preferred_time is None, preferred_time or "")`) rather than
  parsing into `datetime` objects — since `"HH:MM"` strings are zero-padded, plain string comparison
  already sorts them correctly.
- **Conflict detection** intentionally checks for exact time matches rather than full interval
  overlap (e.g., a 30-minute task at 08:00 vs. one starting at 08:15). See `reflection.md` (section
  2b) for the reasoning behind that tradeoff.
- **Recurring tasks** don't track a calendar date — "next occurrence" just means an identical,
  not-yet-completed copy. It relies on whatever schedules tasks to only surface it on the right day.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->