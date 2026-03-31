"""
PawPal+ — backend logic layer.

Classes
-------
Owner       : Represents the pet owner and their daily time budget.
Pet         : Represents a pet and holds its list of care tasks.
Task        : Represents a single pet care task (dataclass).
Scheduler   : Builds a prioritized daily plan given an Owner and their Pet(s).
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
        +urgency_score() int
    }

    class Scheduler {
        +Owner owner
        +int day_start_minute
        +build_plan(pet: Pet) list~ScheduledTask~
        +explain_plan(plan: list~ScheduledTask~) str
    }

    class ScheduledTask {
        +Task task
        +int start_minute
        +int end_minute
        +reason: str
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
    priority: str          # "low" | "medium" | "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "grooming"

    def urgency_score(self) -> int:
        """Return a numeric score used by the Scheduler (higher = more urgent)."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 1)


# ---------------------------------------------------------------------------
# ScheduledTask — a Task placed at a specific time in the daily plan
# ---------------------------------------------------------------------------

@dataclass
class ScheduledTask:
    task: Task
    start_minute: int   # minutes since midnight (e.g. 480 = 8:00 AM)
    end_minute: int
    reason: str = ""

    def time_label(self) -> str:
        """Return a human-readable time range string, e.g. '8:00 AM – 8:20 AM'."""
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
        """Add a care task to this pet's task list."""
        pass  # TODO: implement

    def remove_task(self, task_title: str) -> None:
        """Remove a task by title."""
        pass  # TODO: implement

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return tasks filtered by priority level."""
        pass  # TODO: implement


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
        pass  # TODO: implement

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        pass  # TODO: implement

    def total_task_minutes(self) -> int:
        """Sum the duration of all tasks across all pets."""
        pass  # TODO: implement


# ---------------------------------------------------------------------------
# Scheduler — builds a prioritized daily plan
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, day_start_minute: int = 480) -> None:
        self.owner = owner
        self.day_start_minute = day_start_minute  # default 8:00 AM

    def build_plan(self, pet: Pet) -> list[ScheduledTask]:
        """
        Select and order tasks for *pet* within the owner's available time.

        Strategy:
        - Sort tasks by urgency_score descending (high priority first).
        - Schedule tasks sequentially starting at day_start_minute.
        - Stop when available_minutes is exhausted.
        """
        pass  # TODO: implement

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Return a human-readable explanation of why each task was scheduled."""
        pass  # TODO: implement
