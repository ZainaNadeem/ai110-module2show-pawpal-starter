# PawPal+ Project Reflection

## 1. System Design

### Three core user actions

1. **Add a pet** — the owner enters basic info about themselves (name, available time per day) and their pet (name, species, age) so the system knows who it is planning for.
2. **Add and edit care tasks** — the owner creates tasks like "morning walk", "feeding", or "give medication", specifying how long each takes and how important it is (priority: low / medium / high).
3. **Generate and view today's schedule** — the system produces an ordered daily plan that fits within the owner's available time, shows when each task starts and ends, and explains why each task was included.

---

**a. Initial design**

The initial UML includes four classes:

- **Task** (dataclass) — holds a single care activity: title, duration in minutes, priority level, and category. Exposes an `urgency_score()` method that maps priority to a numeric value so the Scheduler can sort tasks.
- **ScheduledTask** (dataclass) — wraps a Task with a concrete start and end time (minutes since midnight) and a human-readable reason string. The `time_label()` method formats the window as "8:00 AM – 8:20 AM".
- **Pet** — holds the pet's name, species, and age, plus a list of Task objects. Provides `add_task`, `remove_task`, and `get_tasks_by_priority` to manage the task list.
- **Owner** — holds the owner's name and their total available minutes for the day, plus a list of Pet objects. Provides `add_pet`, `remove_pet`, and `total_task_minutes` (sums all tasks across all pets).
- **Scheduler** — the central logic class. Receives an Owner and a day-start time, then calls `build_plan(pet)` to produce a list of ScheduledTask objects sorted by urgency, stopping when the owner's time budget is exhausted. `explain_plan` turns that list into a readable summary.

Relationships: Owner owns one or more Pets; each Pet has zero or more Tasks; Scheduler uses an Owner and creates ScheduledTask objects.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

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
