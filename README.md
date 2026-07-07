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

## ✨ Features

- **Priority/duration scheduling** — `Scheduler.generate_plan()` orders tasks by priority
  (critical > high > medium > low), then by duration, and fits as many as possible into the
  owner's available time window, explaining each decision in a reasoning log.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks chronologically by
  `preferred_time` ("HH:MM"), pushing tasks with no set time to the end instead of erroring.
  Works across a single pet's tasks or every pet the owner has.
- **Filtering** — `Scheduler.filter_tasks()` narrows the task list by completion status and/or
  pet name, independently or combined (e.g., "Milo's incomplete tasks only").
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any two (or more) tasks pinned to
  the exact same time, whether they belong to the same pet or different pets, and returns a plain
  warning message rather than crashing.
- **Daily/weekly recurrence** — `Pet.mark_task_complete()` / `Scheduler.mark_task_complete()`
  automatically spawn a fresh, not-yet-done copy of a task when a `"daily"` or `"weekly"` task is
  completed, so recurring chores keep reappearing without manual re-entry. Completing an
  already-completed task is a safe no-op rather than spawning duplicates.
- **Time-budget skipping** — tasks that would run past the owner's `available_end` are skipped
  (not scheduled) and reported separately, so the plan never silently overflows the day.

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

### Running the tests

```bash
python -m pytest
```

For a coverage report:

```bash
pytest --cov
```

### What the tests cover

The suite lives in `tests/test_pawpal.py` (24 tests) and is organized around the four "Smarter
Scheduling" behaviors described below, plus the core plan-generation logic:

- **Sorting** — chronological ordering by `preferred_time`, tasks with no preferred time sorting
  last, day-boundary times (`00:00`/`23:59`), stable ordering for duplicate times, and an empty
  task list.
- **Recurring tasks** — completing a `"daily"` or `"weekly"` task spawns a fresh, incomplete copy;
  a `"once"` task does not; completing an already-completed task id is a no-op rather than spawning
  a duplicate; `mark_task_complete()` on a missing id or empty pet returns `False` instead of
  raising; the Scheduler-level version searches across every pet the owner has.
- **Filtering** — filtering by completion status and/or pet name, independently and combined, an
  unmatched pet name returning an empty list, and case-insensitive name matching.
- **Plan generation / time budget** — tasks too long for the remaining window get skipped, a
  zero-duration task doesn't hang the scheduler, a zero-minute day skips everything cleanly, and
  already-completed tasks are excluded from the generated plan.
- **Conflict detection** — same-pet and cross-pet conflicts at an identical `preferred_time`,
  three-or-more-way conflicts listing every task involved, completed tasks never being flagged,
  and tasks with no `preferred_time` never being flagged.

### Sample successful run

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/claude
collected 24 items

tests/test_pawpal.py ........................                            [100%]

============================== 24 passed in 0.03s ==============================
```

### Confidence Level

⭐⭐⭐⭐☆ (4/5)

All 24 tests pass, covering sorting, recurrence, filtering, conflict detection, and the core
time-budget scheduling logic, including several edge cases (zero-duration tasks, empty task lists,
already-completed recurring tasks). I'm holding back one star because conflict detection is
intentionally limited to exact time matches rather than true interval overlap (see `reflection.md`,
section 2b) — a known, accepted gap rather than an untested one. I'd also want a few more tests
around malformed input (e.g., an invalid `preferred_time` string) before calling this
production-ready.

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

### Main UI features (Streamlit app)

- **Add pets** — enter a name and species; each pet gets its own independent task list.
- **Add tasks** — set a title, duration, priority, and recurrence (`once`/`daily`/`weekly`), and
  optionally pin the task to a specific time of day.
- **View, sort, and filter tasks** — toggle between time-order and priority-order, and filter the
  visible list by completion status and/or by pet.
- **Mark tasks complete** — a "Mark complete" button per task; completing a recurring task
  automatically adds its next occurrence back onto the list.
- **Conflict check** — a live panel that warns (via `st.warning`) whenever two tasks share the
  same scheduled time, or confirms (via `st.success`) that nothing conflicts.
- **Build a schedule** — generates a full day's plan for a chosen pet, showing the scheduled
  tasks, anything that had to be skipped, any conflicts, and the scheduler's reasoning log.

### Example workflow

1. Add a pet, e.g. "Rex" (dog).
2. Add a task for Rex: "Morning walk," 30 minutes, high priority, pinned to `08:00`.
3. Add a second task at the same time, e.g. "Vet call" at `08:00`, to see the conflict warning
   appear.
4. Switch the sort control to "Time" to see both tasks ordered chronologically instead of by
   priority.
5. Click "Generate schedule" to see the full day's plan, including which tasks were scheduled,
   which were skipped for lack of time, and the conflict warning surfaced again inside the plan.
6. Mark the "Morning walk" task complete — if it were set to `daily`, a fresh copy of it would
   reappear in the task list automatically.

### Key Scheduler behaviors shown

- **Sorting** — `sort_by_time()` puts scrambled tasks back into chronological order.
- **Filtering** — narrowing to one pet's tasks, or only incomplete tasks, or both together.
- **Conflict warnings** — two tasks (same pet or different pets) pinned to the same time both get
  flagged, with no crash.
- **Recurrence** — completing a `daily`/`weekly` task spawns its next occurrence; completing a
  `once` task or an already-completed task does not.

### Sample CLI output (`python main.py`)

```
All tasks, in the order they were added (out of order)
------------------------------------------------------
  [○] 18:00  Evening walk (30min, high)
  [✓] 07:30  Breakfast (10min, critical, daily)
  [○] --:--  Fetch in the yard (20min, low)
  [○] 12:30  Midday potty break (10min, medium)
  [○] 09:00  Litter box scoop (5min, medium, daily)
  [○] 19:00  Evening feeding (10min, high)
  [✓] 08:00  Brushing (15min, low, weekly)

All tasks, sorted chronologically by preferred_time
---------------------------------------------------
  [✓] 07:30  Breakfast (10min, critical, daily)
  [✓] 08:00  Brushing (15min, low, weekly)
  [○] 09:00  Litter box scoop (5min, medium, daily)
  [○] 12:30  Midday potty break (10min, medium)
  [○] 18:00  Evening walk (30min, high)
  [○] 19:00  Evening feeding (10min, high)
  [○] --:--  Fetch in the yard (20min, low)

Incomplete tasks (all pets)
---------------------------
  [○] 18:00  Evening walk (30min, high)
  [○] --:--  Fetch in the yard (20min, low)
  [○] 12:30  Midday potty break (10min, medium)
  [○] 09:00  Litter box scoop (5min, medium, daily)
  [○] 19:00  Evening feeding (10min, high)

Completed tasks (all pets)
--------------------------
  [✓] 07:30  Breakfast (10min, critical, daily)
  [✓] 08:00  Brushing (15min, low, weekly)

Rex's tasks only
----------------
  [○] 18:00  Evening walk (30min, high)
  [✓] 07:30  Breakfast (10min, critical, daily)
  [○] --:--  Fetch in the yard (20min, low)
  [○] 12:30  Midday potty break (10min, medium)

Milo's incomplete tasks only
----------------------------
  [○] 09:00  Litter box scoop (5min, medium, daily)
  [○] 19:00  Evening feeding (10min, high)

Rex's tasks BEFORE completing the daily 'Fetch in the yard'
-------------------------------------------------------------
  [○] 18:00  Evening walk (30min, high)
  [✓] 07:30  Breakfast (10min, critical, daily)
  [○] --:--  Fetch in the yard (20min, low)
  [○] 12:30  Midday potty break (10min, medium)

Rex's tasks AFTER completing it (a fresh occurrence should appear)
----------------------------------------------------------------------
  [○] 18:00  Evening walk (30min, high)
  [✓] 07:30  Breakfast (10min, critical, daily)
  [✓] --:--  Fetch in the yard (20min, low, daily)
  [○] 12:30  Midday potty break (10min, medium)
  [○] --:--  Fetch in the yard (20min, low, daily)

Milo's tasks BEFORE completing the daily litter box scoop
-----------------------------------------------------------
  [○] 09:00  Litter box scoop (5min, medium, daily)
  [○] 19:00  Evening feeding (10min, high)
  [✓] 08:00  Brushing (15min, low, weekly)

Milo's tasks AFTER completing it
--------------------------------
  [✓] 09:00  Litter box scoop (5min, medium, daily)
  [○] 19:00  Evening feeding (10min, high)
  [✓] 08:00  Brushing (15min, low, weekly)
  [○] 09:00  Litter box scoop (5min, medium, daily)

Generated plan for Rex
-----------------------
  Scheduled 'Evening walk' (high priority) from 07:00 to 07:30.
  Scheduled 'Midday potty break' (medium priority) from 07:30 to 07:40.
  Scheduled 'Fetch in the yard' (low priority) from 07:40 to 08:00.

Rex's tasks after adding a same-time conflict
---------------------------------------------
  [○] 18:00  Evening walk (30min, high)
  [✓] 07:30  Breakfast (10min, critical, daily)
  [✓] --:--  Fetch in the yard (20min, low, daily)
  [○] 12:30  Midday potty break (10min, medium)
  [○] --:--  Fetch in the yard (20min, low, daily)
  [○] 12:30  Vet call (15min, medium)

Milo's tasks after adding a cross-pet conflict
------------------------------------------------
  [✓] 09:00  Litter box scoop (5min, medium, daily)
  [○] 19:00  Evening feeding (10min, high)
  [✓] 08:00  Brushing (15min, low, weekly)
  [○] 09:00  Litter box scoop (5min, medium, daily)
  [○] 18:00  Vet appointment prep (10min, high)

Conflict check
--------------
  ⚠ Conflict at 12:30: Rex's 'Midday potty break', Rex's 'Vet call' are all scheduled at the same time.
  ⚠ Conflict at 18:00: Rex's 'Evening walk', Milo's 'Vet appointment prep' are all scheduled at the same time.
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->