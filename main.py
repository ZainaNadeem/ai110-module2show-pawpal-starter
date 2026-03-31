"""
main.py — PawPal+ demo script.

Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # ── Owner ────────────────────────────────────────────────────────────────
    jordan = Owner(name="Jordan", available_minutes=90)

    # ── Pets ─────────────────────────────────────────────────────────────────
    mochi = Pet(name="Mochi", species="dog", age_years=3)
    luna  = Pet(name="Luna",  species="cat", age_years=5)

    jordan.add_pet(mochi)
    jordan.add_pet(luna)

    # ── Tasks for Mochi ──────────────────────────────────────────────────────
    mochi.add_task(Task("Morning walk",   duration_minutes=30, priority="high",   category="walk"))
    mochi.add_task(Task("Breakfast",      duration_minutes=10, priority="high",   category="feeding"))
    mochi.add_task(Task("Training drills",duration_minutes=20, priority="medium", category="enrichment"))
    mochi.add_task(Task("Flea treatment", duration_minutes=5,  priority="high",   category="meds"))

    # ── Tasks for Luna ───────────────────────────────────────────────────────
    luna.add_task(Task("Breakfast",       duration_minutes=5,  priority="high",   category="feeding"))
    luna.add_task(Task("Litter box clean",duration_minutes=10, priority="medium", category="grooming"))
    luna.add_task(Task("Playtime",        duration_minutes=15, priority="low",    category="enrichment"))

    # ── Build and display schedule ────────────────────────────────────────────
    scheduler = Scheduler(owner=jordan, day_start_minute=8 * 60)  # starts at 8:00 AM
    plan = scheduler.build_full_plan()

    print()
    print(scheduler.explain_plan(plan))
    print()

    # Mark one task complete to demonstrate the feature
    if plan:
        plan[0].task.mark_complete()
        print(f"Marked '{plan[0].task.title}' as complete.")
        print(f"Status: completed={plan[0].task.completed}")
    print()

    # Summary stats
    print(f"Total tasks across all pets : {jordan.total_task_minutes()} min worth of tasks")
    print(f"Jordan's time budget today  : {jordan.available_minutes} min")


if __name__ == "__main__":
    main()
