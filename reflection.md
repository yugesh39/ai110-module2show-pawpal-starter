# PawPal+ Project Reflection

## 1. System Design
The three core actions that users can perform in PawPal+ are: (1) Add the owner and pet info, (2) add and editing the task regarding the pet, and (3) creating an schedule based on the owners schedule. The system design should support these actions while ensuring that the scheduling logic is efficient and user-friendly.

**a. Initial design**

Owner — Represents the pet owner and their available time window. Chosen to handle Action 1 (owner info) and because the scheduler needs to know when the owner is free to build a plan.
Pet — Represents the pet and holds its own list of tasks. Chosen to keep pet identity separate from owner, and to group tasks logically under the pet they belong to (supports multi-pet households).
Task — Represents a single care activity (walk, feeding, meds, etc.) with duration and priority. Chosen because it's the core unit of work — everything the scheduler places into the plan is a Task. Covers Action 2 (add/edit tasks).
Scheduler — Pure logic engine that takes an Owner + Pet and produces a plan. Chosen to keep scheduling logic separate from data (Owner/Pet/Task), making it easy to test independently and swap/improve the algorithm without touching the UI. Covers Action 3 (create schedule).


**b. Design changes**

All four relationships from the diagram are present in the skeleton. Nothing's missing structurally



## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

Priority (critical > high > medium > low), duration vs. remaining
available time, preferred time (for anchoring/sorting), completion
status (skips completed tasks), and recurrence frequency (daily/weekly
tasks regenerate). Priority and time budget came first — a pet-care app's main job is making
sure urgent things (meds, feeding) get done before the day runs out of
minutes. Preferred time and recurrence were added next since real
schedules have fixed appointments and repeating chores. Full conflict
overlap was deliberately left simpler (see 2b) since it mattered less
than getting the core priority/time logic right first.

**b. Tradeoffs**

detect_conflicts() flags a conflict only when two tasks share the exact
same preferred_time string. It doesn't check overlapping durations, so
a 30-minute task at 08:00 and another task starting at 08:15 wouldn't be
caught, even though they truly overlap.
Exact-match checking is a simple, fast grouping pass, while true overlap
detection needs interval math and more edge-case handling. For a personal
pet-care app, the realistic failure mode is two tasks accidentally set to
the same clock time — not near-miss overlaps — so the simple check covers
the case that matters most without added complexity.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
