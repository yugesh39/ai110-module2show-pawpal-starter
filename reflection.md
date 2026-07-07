# PawPal+ Project Reflection

## 1. System Design

The three core actions that users can perform in PawPal+ are: (1) add the owner and pet info,
(2) add and edit tasks for a pet, and (3) generate a schedule based on the owner's availability.
The system design should support these actions while ensuring that the scheduling logic is
efficient and user-friendly.

**a. Initial design**

- **Owner** — Represents the pet owner and their available time window. Chosen to handle Action 1
  (owner info) and because the scheduler needs to know when the owner is free to build a plan.
- **Pet** — Represents the pet and holds its own list of tasks. Chosen to keep pet identity
  separate from owner, and to group tasks logically under the pet they belong to (supports
  multi-pet households).
- **Task** — Represents a single care activity (walk, feeding, meds, etc.) with duration and
  priority. Chosen because it's the core unit of work — everything the scheduler places into the
  plan is a Task. Covers Action 2 (add/edit tasks).
- **Scheduler** — Pure logic engine that takes an Owner + Pet and produces a plan. Chosen to keep
  scheduling logic separate from data (Owner/Pet/Task), making it easy to test independently and
  swap/improve the algorithm without touching the UI. Covers Action 3 (create schedule).

**b. Design changes**

All four relationships from the diagram are present in the final code, so nothing's missing
structurally. What did grow beyond the original diagram was the *method surface* on `Task`,
`Pet`, and `Scheduler` — `completed`/`frequency` fields, `next_occurrence()`, `mark_task_complete()`
(at both the `Pet` and `Scheduler` level), `sort_by_time()`, `filter_tasks()`, and
`detect_conflicts()` were all added during the build as new requirements (recurrence, conflicts,
filtering) came in. The final UML in `diagrams/uml_final.mmd` documents all of this, including a
note on the fact that `Scheduler` is constructed with one owner + one pet but most of its methods
actually operate across every pet the owner has — an asymmetry that wasn't obvious from the
original class boxes alone.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

Priority (critical > high > medium > low), duration vs. remaining available time, preferred time
(for anchoring/sorting), completion status (skips completed tasks), and recurrence frequency
(daily/weekly tasks regenerate). Priority and time budget came first — a pet-care app's main job
is making sure urgent things (meds, feeding) get done before the day runs out of minutes.
Preferred time and recurrence were added next since real schedules have fixed appointments and
repeating chores. Full conflict overlap was deliberately left simpler (see 2b) since it mattered
less than getting the core priority/time logic right first.

**b. Tradeoffs**

`detect_conflicts()` flags a conflict only when two tasks share the exact same `preferred_time`
string. It doesn't check overlapping durations, so a 30-minute task at 08:00 and another task
starting at 08:15 wouldn't be caught, even though they truly overlap. Exact-match checking is a
simple, fast grouping pass, while true overlap detection needs interval math and more edge-case
handling. For a personal pet-care app, the realistic failure mode is two tasks accidentally set to
the same clock time — not near-miss overlaps — so the simple check covers the case that matters
most without added complexity.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across the full lifecycle, not just for writing code: brainstorming
algorithm/logic improvements before touching the implementation, drafting method bodies once the
approach was agreed on, generating a test plan and then the tests themselves, drafting README/UML
documentation from the final code, and reviewing my own "completed" methods a second time by
asking directly whether they could be simplified.

The most effective use, by far, was **treating it as a second reviewer rather than a first
author**: writing (or sketching) the logic myself, then asking "how would you simplify this?" or
"what edge cases am I missing?" surfaced real gaps — most notably, a written test plan turned up
an actual bug (`mark_task_complete()` spawning a duplicate occurrence when called twice on an
already-completed task id) that the demo script had never exercised. The prompts that worked best
were narrow and concrete — "what are the edge cases for X" or "simplify this specific method" —
rather than open-ended requests like "improve my scheduler," which tend to produce generic advice
instead of something tied to the actual code.

**b. Judgment and verification**

One clear example: when I asked for a "more Pythonic" rewrite of `sort_by_time()`, the suggested
version used `operator.attrgetter("preferred_time") or ""` as the sort key. It looked terser and
more idiomatic, but it's actually broken — `attrgetter(...)` returns a callable object, which is
always truthy, so the `or ""` fallback never executes, and `sorted()` would still crash comparing
`None` against a string for any task with no `preferred_time`. I rejected it and kept the original
two-part tuple key (`(preferred_time is None, preferred_time or "")`), which is both correct and,
if anything, easier to read since the boolean explicitly names what's being checked. A second,
similar case came up with `detect_conflicts()`: a `defaultdict` + list-comprehension rewrite was
functionally correct but compressed the warning-message formatting into a single dense line,
trading real readability for brevity with no performance benefit on a list this small — I only
kept the one genuinely useful piece of it (`defaultdict` instead of `setdefault`) and left the
rest as an explicit loop.

I verified suggestions the same way both times: by actually running them, not by reading and
trusting them. The `attrgetter` bug wasn't obvious from just looking at the line — running it
against a task with `preferred_time=None` would have raised immediately. That's become my default
now: treat "looks idiomatic" and "is correct" as two separate questions.

**c. Separate chat sessions**

Splitting work into separate chat sessions by *phase* (algorithmic brainstorming, then core
implementation, then a dedicated testing-only session) kept each conversation focused on one kind
of thinking instead of blending them. The testing session in particular benefited from not having
the implementation reasoning still "in the room" — approaching `pawpal_system.py` fresh, purely
to ask "what could break this," found the double-completion bug that writing the feature in the
first place had missed, precisely because I wasn't anchored to my own assumptions about how
`mark_task_complete()` would be used. Keeping planning, building, and testing in separate threads
also made it easier to go back and check "wait, why did I decide this?" without scrolling through
an enormous mixed conversation.

---

## 4. Testing and Verification

**a. What you tested**

The test suite (`tests/test_pawpal.py`, 24 tests) covers five areas: sorting (chronological order,
missing/tied/boundary times, empty lists), recurring tasks (daily/weekly spawning a fresh
occurrence, `once` tasks not recurring, double-completion being a no-op, missing task ids),
filtering (by status and/or pet name, case-insensitivity, unmatched names), plan generation and
time budget (tasks too long for the window, zero-duration tasks, zero-minute days, completed tasks
excluded), and conflict detection (same-pet and cross-pet conflicts, three-way conflicts,
completed/timeless tasks never flagged). These mattered because they're exactly the places where
"looks right in the demo" and "actually correct" diverge — a scheduler only really gets exercised
when someone tries the weird input, not the happy path.

**b. Confidence**

4 out of 5 stars, same rating as in the README. All 24 tests pass, and they cover real edge cases,
not just the obvious ones. The gap to 5 stars is intentional and known rather than a blind spot:
conflict detection's exact-time-match tradeoff (section 2b) is accepted, not tested-around, and I
haven't yet written tests for malformed input — an invalid `preferred_time` string that doesn't
match `"HH:MM"`, for instance, would currently raise inside `datetime.strptime` rather than fail
gracefully. That's the next thing I'd test if I had more time, along with concurrent edits (two
`mark_task_complete()` calls on different task ids for the same pet in quick succession) and
larger-scale performance (does `detect_conflicts()` still feel "lightweight" with hundreds of
tasks, or does the O(n) grouping start to matter).

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the recurrence and conflict-detection features turned out end to end —
not just that they work, but that the test-writing process itself caught a real bug
(double-completing a task spawning a duplicate) before it reached the UI. That felt like the
system working as intended: write the feature, write tests that assume nothing, let the tests do
their job.

**b. What you would improve**

Given another iteration, I'd upgrade `detect_conflicts()` from exact-time matching to genuine
interval overlap now that the simpler version has proven the concept, add validation on
`preferred_time` input (so a malformed string fails with a clear error instead of an obscure
`strptime` crash), and add a real date dimension to recurring tasks instead of the current
"identical, not-yet-done copy" model, which relies entirely on the caller to only surface tasks on
the right day.

**c. Key takeaway**

The biggest lesson was that being the "lead architect" means the AI's suggestions are proposals,
not decisions — every one still needs to be run, not just read, before it goes in. The two
rejected "Pythonic" rewrites in this project were both plausible-looking and both wrong or worse
in a way that only showed up when actually executed. My job wasn't to write every line myself; it
was to hold the design intent (clarity over cleverness, correctness over idiom) and use that as
the filter for what to accept, reject, or reshape — the AI is fast at generating options, but
deciding which option actually fits the system is still mine to do.