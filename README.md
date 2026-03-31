# PawPal+ — Pet Care Planning Assistant

PawPal+ is a Streamlit app that helps a busy pet owner plan daily care tasks for one or more pets. You enter your available time for the day, register your pets, and add care tasks with priorities. The built-in scheduler automatically builds a time-ordered plan that fits your schedule — and tells you exactly why each task was chosen.

---

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that:

- Tracks pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Considers constraints (time available, priority)
- Produces a daily plan and explains why it chose that plan

---

## Features

### Priority-based scheduling
Tasks are ranked by urgency score (`high = 3`, `medium = 2`, `low = 1`). The scheduler sorts all tasks globally across every pet by this score before building the timeline, so a high-priority medication task for one pet will always be scheduled before a low-priority playtime for another.

### Time-budget enforcement
The owner sets a total available-minutes budget for the day. The scheduler walks the sorted task list sequentially and skips any task that would exceed the remaining budget — it never overbooks. The UI shows a real-time progress bar and a precise "over budget by N min" warning so the owner knows exactly what needs to be cut.

### Conflict detection and skip warnings
If any tasks can't fit in the budget, the app lists each skipped task by name, priority, and duration, and tells the owner which action would resolve the conflict (raise budget or remove a lower-priority task).

### Multi-pet support
An owner can register any number of pets. `Scheduler.build_full_plan()` collects tasks from every pet and schedules them in a single globally-sorted timeline, interleaving pets as needed.

### Sorted task list
The task table in Section 3 is sorted by priority (high → low), mirroring exactly the order the scheduler would process them. This makes it easy to spot whether a low-priority task is taking up too much time.

### Readable plan output
Each scheduled task displays a human-readable time window (`8:00 AM – 8:30 AM`), an expandable "Why was this task scheduled?" panel, and a full plain-text explanation via `Scheduler.explain_plan()`.

### Persistent session state
Streamlit reruns the script on every interaction. `st.session_state` stores the `Owner` object between reruns so pets and tasks are never lost when clicking buttons.

---

## Project structure

```
pawpal_system.py   — logic layer: Owner, Pet, Task, Scheduler, ScheduledTask
app.py             — Streamlit UI that imports and calls the logic layer
main.py            — terminal demo script (python main.py)
tests/
  test_pawpal.py   — 11 pytest tests covering all core behaviours
uml_final.md       — final Mermaid class diagram with design notes
reflection.md      — structured project reflection
requirements.txt   — Python dependencies
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

To run the terminal demo:

```bash
python main.py
```

To run tests:

```bash
python -m pytest tests/ -v
```

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

---

## UML Class Diagram

See [`uml_final.md`](uml_final.md) for the Mermaid source and design notes. Paste the diagram into [mermaid.live](https://mermaid.live) to render and export as PNG.

---

## Class responsibilities

| Class | Responsibility |
|---|---|
| `Task` | Single care activity with title, duration, priority, category, and completion state |
| `ScheduledTask` | A Task placed at a specific time slot in the daily plan |
| `Pet` | Holds a pet's profile and its list of Tasks |
| `Owner` | Manages multiple Pets and tracks the daily time budget |
| `Scheduler` | Sorts tasks by urgency, schedules them within the budget, and explains the plan |
