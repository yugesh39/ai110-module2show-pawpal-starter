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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
