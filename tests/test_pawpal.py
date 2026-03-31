"""Tests for PawPal+ core logic."""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_task():
    return Task(title="Morning walk", duration_minutes=30, priority="high", category="walk")


@pytest.fixture
def sample_pet():
    return Pet(name="Mochi", species="dog", age_years=3)


@pytest.fixture
def sample_owner(sample_pet):
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(sample_pet)
    return owner


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(sample_task):
    """Calling mark_complete() should flip completed from False to True."""
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True


def test_urgency_score_values():
    """urgency_score should return 3 for high, 2 for medium, 1 for low."""
    assert Task("a", 10, "high").urgency_score() == 3
    assert Task("b", 10, "medium").urgency_score() == 2
    assert Task("c", 10, "low").urgency_score() == 1


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count(sample_pet, sample_task):
    """Adding a task to a Pet should increase its task count by 1."""
    before = len(sample_pet.tasks)
    sample_pet.add_task(sample_task)
    assert len(sample_pet.tasks) == before + 1


def test_remove_task_decreases_count(sample_pet, sample_task):
    """Removing a task by title should decrease the task count by 1."""
    sample_pet.add_task(sample_task)
    before = len(sample_pet.tasks)
    sample_pet.remove_task(sample_task.title)
    assert len(sample_pet.tasks) == before - 1


def test_get_tasks_by_priority(sample_pet):
    """get_tasks_by_priority should return only tasks with the given priority."""
    sample_pet.add_task(Task("Walk", 20, "high"))
    sample_pet.add_task(Task("Feed", 10, "medium"))
    sample_pet.add_task(Task("Play", 15, "low"))

    high_tasks = sample_pet.get_tasks_by_priority("high")
    assert len(high_tasks) == 1
    assert high_tasks[0].title == "Walk"


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

def test_add_pet_increases_count():
    """add_pet should register the pet under the owner."""
    owner = Owner("Alex", available_minutes=60)
    pet = Pet("Buddy", "dog")
    assert len(owner.pets) == 0
    owner.add_pet(pet)
    assert len(owner.pets) == 1


def test_total_task_minutes_sums_across_pets():
    """total_task_minutes should sum durations from all pets."""
    owner = Owner("Sam", available_minutes=200)
    dog = Pet("Rex", "dog")
    cat = Pet("Nala", "cat")
    dog.add_task(Task("Walk", 30, "high"))
    cat.add_task(Task("Feed", 10, "medium"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert owner.total_task_minutes() == 40


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_build_plan_respects_time_budget():
    """Scheduled tasks should not exceed the owner's available_minutes."""
    owner = Owner("Jordan", available_minutes=40)
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk",  30, "high"))
    pet.add_task(Task("Train", 20, "medium"))   # won't fit: 30+20 > 40
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.build_plan(pet)

    total = sum(st.task.duration_minutes for st in plan)
    assert total <= owner.available_minutes


def test_build_plan_orders_by_priority():
    """Higher-priority tasks should appear before lower-priority ones in the plan."""
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Play",  15, "low"))
    pet.add_task(Task("Meds",  10, "high"))
    pet.add_task(Task("Train", 20, "medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.build_plan(pet)

    priorities = [st.task.priority for st in plan]
    score = lambda p: {"high": 3, "medium": 2, "low": 1}[p]
    scores = [score(p) for p in priorities]
    assert scores == sorted(scores, reverse=True), "Plan should be sorted high → low priority"


def test_explain_plan_returns_string():
    """explain_plan should return a non-empty string for a non-empty plan."""
    owner = Owner("Jordan", available_minutes=60)
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.build_plan(pet)
    explanation = scheduler.explain_plan(plan)

    assert isinstance(explanation, str)
    assert len(explanation) > 0


def test_explain_plan_empty_returns_message():
    """explain_plan with an empty plan should return a helpful message."""
    owner = Owner("Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    result = scheduler.explain_plan([])
    assert "No tasks" in result
