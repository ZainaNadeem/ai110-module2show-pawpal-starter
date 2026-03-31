# PawPal+ Project Reflection

## 1. System Design

### Three core user actions

1. **Add a pet** — the owner enters basic info about themselves (name, available time per day) and their pet (name, species, age) so the system knows who it is planning for.
2. **Add and edit care tasks** — the owner creates tasks like "morning walk", "feeding", or "give medication", specifying how long each takes and how important it is (priority: low / medium / high).
3. **Generate and view today's schedule** — the system produces an ordered daily plan that fits within the owner's available time, shows when each task starts and ends, and explains why each task was included.

---

**a. Initial design**

The initial UML includes five classes:

- **Task** (dataclass) — holds a single care activity: title, duration in minutes, priority level, and category. Exposes an `urgency_score()` method that maps priority to a numeric value so the Scheduler can sort tasks.
- **ScheduledTask** (dataclass) — wraps a Task with a concrete start and end time (minutes since midnight) and a human-readable reason string. The `time_label()` method formats the window as "8:00 AM – 8:20 AM".
- **Pet** — holds the pet's name, species, and age, plus a list of Task objects. Provides `add_task`, `remove_task`, and `get_tasks_by_priority` to manage the task list.
- **Owner** — holds the owner's name and their total available minutes for the day, plus a list of Pet objects. Provides `add_pet`, `remove_pet`, and `total_task_minutes` (sums all tasks across all pets).
- **Scheduler** — the central logic class. Receives an Owner and a day-start time, then calls `build_plan(pet)` to produce a list of ScheduledTask objects sorted by urgency, stopping when the owner's time budget is exhausted. `explain_plan` turns that list into a readable summary.

Relationships: Owner owns one or more Pets; each Pet has zero or more Tasks; Scheduler uses an Owner and creates ScheduledTask objects.

**b. Design changes**

Yes, the design changed in four meaningful ways during implementation:

1. **Added `bool completed` and `mark_complete()` to `Task`** — The initial design treated tasks as purely descriptive. Once the UI needed to show which tasks were done, a completion flag became essential. `mark_complete()` was added as the only way to flip it, keeping the state change explicit.

2. **Added `all_tasks()` to `Owner`** — The initial `Owner` only offered `total_task_minutes()`. When the Scheduler needed to iterate over every (pet, task) pair across all pets to build a global plan, a helper that returns those pairs was cleaner than nesting two loops inside `Scheduler` itself.

3. **Added `build_full_plan()` to `Scheduler`** — The original `build_plan(pet)` operated on a single pet. Once multi-pet support was required, a second method that collects tasks from all pets, sorts them globally, and schedules them in one unified timeline was added rather than calling `build_plan` once per pet (which would have treated each pet's budget independently and produced incorrect results).

4. **Added `pet_name: str` to `ScheduledTask`** — In a single-pet design this field is redundant, but a multi-pet plan displayed in one table needs to label which pet each row belongs to. Adding the field to the dataclass kept the UI layer simple.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints:

- **Time budget** — the owner's `available_minutes` is a hard ceiling. No combination of scheduled tasks may exceed it. This was treated as the primary constraint because a pet care plan that overruns the owner's real availability is useless.
- **Task priority** — tasks are ranked high (3) > medium (2) > low (1). The scheduler sorts by this score before consuming the budget, so the most critical tasks (medications, feeding) are always placed first.

Time budget was chosen as the binding constraint because it is objective and measurable. Priority determines the order within that constraint.

**b. Tradeoffs**

The scheduler uses a greedy, first-fit algorithm: it iterates the priority-sorted task list and skips any task that would push `time_used` past `available_minutes`, then continues looking for smaller tasks that might still fit. This means a single large high-priority task can effectively block several smaller medium-priority tasks from filling the remaining gap.

This tradeoff is reasonable for a daily pet care context because:
- The planning horizon is short (one day), so the greedy approach produces a correct plan for typical inputs.
- Pet owners generally care more about doing the right things (high priority) than fitting in the maximum number of tasks. Correctly scheduling fewer, more important tasks is preferable to scheduling more tasks of mixed importance.
- The skipped-task warning in the UI lets the owner see exactly what was dropped and why, making the tradeoff transparent rather than hidden.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools (Claude Code / VS Code Copilot) were used across every phase:

- **Design brainstorming (Phase 1)** — Asked the AI to generate a Mermaid class diagram from a natural-language description of the four classes. This produced a useful first draft quickly, though the relationship arrows needed manual correction (initial draft used generic associations everywhere; composition was more appropriate for Owner→Pet and Pet→Task).
- **Skeleton generation (Phase 2)** — Used agent mode to produce method stubs with docstrings from the UML. This saved time on boilerplate and kept the code consistent with the diagram.
- **Logic implementation (Phase 3)** — Asked the AI "how should the Scheduler retrieve all tasks from the Owner's pets?" to clarify the cross-class communication pattern before writing `all_tasks()` and `build_full_plan()`.
- **Test generation (Phase 3)** — Used the AI to draft pytest fixtures and test cases, then reviewed each one to confirm it tested behaviour (not implementation details) and was not trivially always-passing.
- **UI refinement (Phase 4)** — Asked the AI to suggest clearer Streamlit components for displaying priority levels and conflict warnings. The `_budget_bar()` helper and the skipped-task warning block came from this session.

The most effective prompts were specific and file-grounded: referencing `#file:pawpal_system.py` and asking a narrow question ("what is missing from this design?") produced more useful output than open-ended requests.

**b. Judgment and verification**

During test generation, the AI produced a test that checked `len(plan) > 0` after calling `build_full_plan()` on an owner with tasks. This test would always pass even if the scheduler had a bug — it only verifies that the function returns something, not that the returned plan is correct. The test was replaced with `test_build_plan_orders_by_priority`, which extracts the priority list from the plan and asserts it is sorted highest-to-lowest. This tests the actual scheduling behaviour, not just the return type.

The AI suggestion was evaluated by asking: "What real bug would this test catch?" If the answer is "none," the test is not useful.

---

## 4. Testing and Verification

**a. What you tested**

Eleven tests cover the following behaviours:

| Test | Behaviour verified |
|---|---|
| `test_mark_complete_changes_status` | `Task.mark_complete()` flips `completed` to `True` |
| `test_urgency_score_values` | Score mapping: high=3, medium=2, low=1 |
| `test_add_task_increases_count` | `Pet.add_task()` appends to the task list |
| `test_remove_task_decreases_count` | `Pet.remove_task()` removes by title |
| `test_get_tasks_by_priority` | Filter returns only matching-priority tasks |
| `test_add_pet_increases_count` | `Owner.add_pet()` registers the pet |
| `test_total_task_minutes_sums_across_pets` | Cross-pet summation is correct |
| `test_build_plan_respects_time_budget` | Scheduled total never exceeds `available_minutes` |
| `test_build_plan_orders_by_priority` | Plan is sorted high → low priority |
| `test_explain_plan_returns_string` | Explanation is a non-empty string |
| `test_explain_plan_empty_returns_message` | Empty plan returns a helpful message |

These tests matter because the scheduler's two core guarantees — "stay within budget" and "schedule by priority" — must hold for the app to be trustworthy. A bug in either would silently produce wrong plans without the tests catching it.

**b. Confidence**

Confidence is high for the happy-path behaviours covered by the tests. Edge cases that would be tested next with more time:

- What happens when two tasks have exactly equal urgency scores and only one fits?
- What if `available_minutes` is 0?
- What if a single task's `duration_minutes` exceeds the entire budget?
- What if the same pet is registered twice under the same Owner?
- What if `mark_complete()` is called twice on the same task?

---

## 5. Reflection

**a. What went well**

The separation between the logic layer (`pawpal_system.py`) and the UI (`app.py`) worked well in practice. Because `Scheduler` and the other classes had no Streamlit imports, they could be tested with pytest without needing a browser, and the UI could be rewritten or redesigned without touching any scheduling logic. This separation also made it easy to use `main.py` as a quick terminal sanity-check before opening the browser.

**b. What you would improve**

The current scheduler is greedy and does not backtrack. If a 60-minute task takes the first slot and there are two 30-minute tasks that together would have fit, those two tasks are skipped entirely. A small dynamic-programming or branch-and-bound approach would find a tighter packing. For a production app, this would be worth implementing.

Additionally, tasks currently have no time-of-day constraints. "Medication at 8 AM" and "evening walk at 6 PM" are treated identically. Adding a `preferred_time` field to `Task` and a time-window constraint to `Scheduler` would make the plans much more realistic.

**c. Key takeaway**

The most important thing learned about designing systems with AI assistance is that the AI is an excellent *drafter* but a poor *architect*. It can turn a description into a diagram, a diagram into code, and code into tests — quickly and accurately. But it does not know which constraints matter most, which tradeoffs are acceptable for a given user, or when a technically valid suggestion produces a fragile design. Staying in the architect role — deciding what the system should do, reviewing every AI output against that intent, and pushing back when a suggestion adds complexity without adding value — is what makes AI-assisted development produce good software rather than just a lot of code.

**AI tool-specific reflection (VS Code Copilot):**

- **Most effective features**: Inline Chat on a specific method stub ("implement this using the strategy described in the docstring") produced tight, on-target code. Agent mode with `#file:` references was more effective than open-ended chat because it grounded suggestions in the actual codebase.
- **One rejected suggestion**: Copilot suggested adding a `__post_init__` validator to the `Task` dataclass that would raise `ValueError` for unknown priority strings. This was rejected because the urgency_score method already handles unknown values by defaulting to 1, adding a validator would break existing test fixtures that pass in-progress data, and the extra complexity wasn't justified for a class-project scope.
- **Separate sessions per phase**: Using a new Copilot chat for each phase (design, implementation, testing, UI) prevented earlier context from bleeding into later decisions. When working on tests, the chat only knew about the implementation — not the design rationale — which forced the tests to be written against observable behaviour rather than against internal implementation details.
