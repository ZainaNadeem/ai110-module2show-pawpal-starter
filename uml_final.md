# PawPal+ — Final UML Class Diagram

> Paste the Mermaid block below into [https://mermaid.live](https://mermaid.live) and export as PNG to produce `uml_final.png`.

```mermaid
classDiagram
    direction TB

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +bool completed
        +urgency_score() int
        +mark_complete() None
    }

    class ScheduledTask {
        +Task task
        +str pet_name
        +int start_minute
        +int end_minute
        +str reason
        +time_label() str
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

    class Owner {
        +str name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +remove_pet(pet_name: str) None
        +all_tasks() list~tuple~
        +total_task_minutes() int
    }

    class Scheduler {
        +Owner owner
        +int day_start_minute
        +build_plan(pet: Pet) list~ScheduledTask~
        +build_full_plan() list~ScheduledTask~
        +explain_plan(plan: list~ScheduledTask~) str
    }

    Owner "1" *-- "1..*" Pet : owns
    Pet "1" *-- "0..*" Task : has
    ScheduledTask "1" --> "1" Task : wraps
    Scheduler "1" --> "1" Owner : reads budget from
    Scheduler ..> ScheduledTask : creates
```

## Design notes

| Relationship | Type | Reason |
|---|---|---|
| Owner → Pet | Composition (`*--`) | Pets are created and managed through the Owner |
| Pet → Task | Composition (`*--`) | Tasks belong to exactly one pet |
| ScheduledTask → Task | Association (`-->`) | ScheduledTask wraps a Task without owning it |
| Scheduler → Owner | Dependency (`-->`) | Scheduler reads the budget; does not own the Owner |
| Scheduler ⇢ ScheduledTask | Usage (`..>`) | Scheduler instantiates ScheduledTask objects and returns them |

## Changes from the initial draft

| Change | Reason |
|---|---|
| Added `bool completed` and `mark_complete()` to `Task` | Needed to track task completion in the UI |
| Added `all_tasks()` to `Owner` | Scheduler needed a flat list of all (pet, task) pairs across all pets |
| Added `build_full_plan()` to `Scheduler` | Single-pet `build_plan()` was insufficient once multi-pet scheduling was required |
| Added `str pet_name` to `ScheduledTask` | Multi-pet plans needed to label which pet each task belongs to |
| Tightened relationship arrows to Composition where appropriate | Initial draft used generic associations everywhere |
