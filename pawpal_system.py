"""
PawPal+ — backend logic layer.

Classes
-------
Owner        : Represents the pet owner and their daily time budget.
Pet          : Represents a pet and holds its list of care tasks.
Task         : Represents a single pet care task (dataclass).
Scheduler    : Builds a prioritized daily plan given an Owner and their Pet(s).
ScheduledTask: Represents a task placed at a specific time in the plan (dataclass).

Mermaid class diagram (paste into https://mermaid.live to preview):

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +remove_pet(pet_name: str) None
        +total_task_minutes() int
        +all_tasks() list~Task~
    }

    class Pet {
        +str name
        +str species
        +int age_years
        +list~Task~ tasks
        +add_task(task: Task) None
        +remove_task(task_title: str) None
        +get_tasks_by_priority(priority: str) list~Task~
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +bool completed
        +urgency_score() int
        +mark_complete() None
    }

    class Scheduler {
        +Owner owner
        +int day_start_minute
        +build_plan(pet: Pet) list~ScheduledTask~
        +build_full_plan() list~ScheduledTask~
        +explain_plan(plan: list~ScheduledTask~) str
    }

    class ScheduledTask {
        +Task task
        +str pet_name
        +int start_minute
        +int end_minute
        +str reason
        +time_label() str
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : uses
    Scheduler ..> ScheduledTask : creates
```
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Task — a single pet care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "grooming"
    completed: bool = False

    def urgency_score(self) -> int:
        """Return a numeric priority score (3=high, 2=medium, 1=low) for sorting."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 1)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


# ---------------------------------------------------------------------------
# ScheduledTask — a Task placed at a specific time in the daily plan
# ---------------------------------------------------------------------------

@dataclass
class ScheduledTask:
    task: Task
    start_minute: int   # minutes since midnight (e.g. 480 = 8:00 AM)
    end_minute: int
    pet_name: str = ""
    reason: str = ""

    def time_label(self) -> str:
        """Return a human-readable time range such as '8:00 AM – 8:20 AM'."""
        def fmt(minutes: int) -> str:
            h, m = divmod(minutes, 60)
            period = "AM" if h < 12 else "PM"
            h = h % 12 or 12
            return f"{h}:{m:02d} {period}"

        return f"{fmt(self.start_minute)} – {fmt(self.end_minute)}"


# ---------------------------------------------------------------------------
# Pet — represents a pet and its care task list
# ---------------------------------------------------------------------------

class Pet:
    def __init__(self, name: str, species: str, age_years: int = 0) -> None:
        self.name = name
        self.species = species
        self.age_years = age_years
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove the first task whose title matches (case-insensitive)."""
        self.tasks = [t for t in self.tasks if t.title.lower() != task_title.lower()]

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return all tasks whose priority matches the given level."""
        return [t for t in self.tasks if t.priority == priority]

    def __repr__(self) -> str:  # pragma: no cover
        return f"Pet(name={self.name!r}, species={self.species!r}, tasks={len(self.tasks)})"


# ---------------------------------------------------------------------------
# Owner — represents the pet owner and their available time
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_minutes: int = 120) -> None:
        self.name = name
        self.available_minutes = available_minutes  # total free time today
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name (case-insensitive)."""
        self.pets = [p for p in self.pets if p.name.lower() != pet_name.lower()]

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all registered pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def total_task_minutes(self) -> int:
        """Sum the duration of all tasks across all pets."""
        return sum(task.duration_minutes for _, task in self.all_tasks())

    def __repr__(self) -> str:  # pragma: no cover
        return f"Owner(name={self.name!r}, pets={len(self.pets)}, available={self.available_minutes}min)"


# ---------------------------------------------------------------------------
# Scheduler — builds a prioritized daily plan
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, day_start_minute: int = 480) -> None:
        self.owner = owner
        self.day_start_minute = day_start_minute  # default 8:00 AM

    def build_plan(self, pet: Pet) -> list[ScheduledTask]:
        """
        Build a time-ordered plan for a single pet within the owner's time budget.

        Tasks are sorted by urgency_score (highest first), then scheduled
        sequentially. Scheduling stops when the owner's available_minutes
        would be exceeded by adding another task.
        """
        sorted_tasks = sorted(pet.tasks, key=lambda t: t.urgency_score(), reverse=True)

        plan: list[ScheduledTask] = []
        cursor = self.day_start_minute
        time_used = 0

        for task in sorted_tasks:
            if time_used + task.duration_minutes > self.owner.available_minutes:
                continue  # skip tasks that don't fit in remaining budget
            reason = (
                f"Priority '{task.priority}' task for {pet.name}; "
                f"fits within {self.owner.name}'s remaining time."
            )
            st = ScheduledTask(
                task=task,
                start_minute=cursor,
                end_minute=cursor + task.duration_minutes,
                pet_name=pet.name,
                reason=reason,
            )
            plan.append(st)
            cursor += task.duration_minutes
            time_used += task.duration_minutes

        return plan

    def build_full_plan(self) -> list[ScheduledTask]:
        """
        Build a combined plan across all of the owner's pets.

        Pulls tasks from every pet, sorts them globally by urgency, and
        schedules them sequentially within the owner's available_minutes.
        """
        # Collect all (urgency, pet, task) triples
        all_items = [
            (task.urgency_score(), pet, task)
            for pet in self.owner.pets
            for task in pet.tasks
        ]
        all_items.sort(key=lambda x: x[0], reverse=True)

        plan: list[ScheduledTask] = []
        cursor = self.day_start_minute
        time_used = 0

        for _, pet, task in all_items:
            if time_used + task.duration_minutes > self.owner.available_minutes:
                continue
            reason = (
                f"Priority '{task.priority}' task for {pet.name}; "
                f"fits within {self.owner.name}'s remaining time."
            )
            st = ScheduledTask(
                task=task,
                start_minute=cursor,
                end_minute=cursor + task.duration_minutes,
                pet_name=pet.name,
                reason=reason,
            )
            plan.append(st)
            cursor += task.duration_minutes
            time_used += task.duration_minutes

        return plan

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Return a formatted string explaining each scheduled task and its reasoning."""
        if not plan:
            return "No tasks could be scheduled within the available time."

        lines = [f"Daily Plan for {self.owner.name}\n" + "=" * 40]
        for st in plan:
            status = "[done]" if st.task.completed else "[ ]"
            lines.append(
                f"{status} {st.time_label()}  |  {st.pet_name}: {st.task.title}"
                f"  ({st.task.duration_minutes} min, {st.task.priority} priority)\n"
                f"      Reason: {st.reason}"
            )
        total = sum(st.task.duration_minutes for st in plan)
        lines.append(f"\nTotal scheduled: {total} min  |  Budget: {self.owner.available_minutes} min")
        return "\n".join(lines)
