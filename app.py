"""
app.py — PawPal+ Streamlit UI.

Connects the Owner / Pet / Task / Scheduler logic layer to an interactive UI.
st.session_state acts as the persistent "vault" that survives page reruns.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialisation — runs only the first time
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "last_plan" not in st.session_state:
    st.session_state.last_plan = []

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
CATEGORY_ICON = {
    "walk": "🦮", "feeding": "🍽️", "meds": "💊",
    "grooming": "✂️", "enrichment": "🎾", "general": "📋",
}


def _budget_bar(owner: Owner) -> None:
    """Render a colour-coded progress bar showing time budget usage."""
    total = owner.total_task_minutes()
    budget = owner.available_minutes
    used_pct = min(total / budget, 1.0) if budget else 0

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Tasks total", f"{total} min")
    col_b.metric("Budget", f"{budget} min")
    delta = budget - total
    col_c.metric("Remaining", f"{delta} min", delta=delta, delta_color="normal")

    st.progress(used_pct)

    if total > budget:
        over = total - budget
        st.warning(
            f"⚠️ **Time conflict:** Your tasks total **{total} min** but you only have "
            f"**{budget} min** available — that's **{over} min over budget**. "
            "The scheduler will skip the lowest-priority tasks that don't fit. "
            "Consider raising your time budget or removing lower-priority tasks."
        )
    elif used_pct >= 0.9:
        st.info("📌 You're using more than 90 % of your time budget today.")


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------

st.title("🐾 PawPal+")
st.caption("Your daily pet care planning assistant.")

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------

st.header("1. Owner Info")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name", value="Jordan")
    with col2:
        available_minutes = st.number_input(
            "Available minutes today", min_value=10, max_value=480, value=120, step=10
        )
    submitted_owner = st.form_submit_button("Save owner")

if submitted_owner:
    existing_pets = st.session_state.owner.pets if st.session_state.owner else []
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    for pet in existing_pets:
        st.session_state.owner.add_pet(pet)
    st.session_state.last_plan = []   # reset plan when owner changes
    st.success(f"Owner saved: **{owner_name}** — {available_minutes} min available today.")

if st.session_state.owner:
    o = st.session_state.owner
    st.info(f"**{o.name}** · {o.available_minutes} min budget · {len(o.pets)} pet(s) registered")
else:
    st.warning("Fill in your name above and click **Save owner** to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2 — Add a pet
# ---------------------------------------------------------------------------

st.divider()
st.header("2. Add a Pet")

with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    with col3:
        age_years = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    new_pet = Pet(name=pet_name, species=species, age_years=int(age_years))
    owner.add_pet(new_pet)
    st.session_state.last_plan = []
    st.success(f"Added **{pet_name}** the {species}!")

if owner.pets:
    st.subheader("Registered pets")
    for pet in owner.pets:
        high = len(pet.get_tasks_by_priority("high"))
        med  = len(pet.get_tasks_by_priority("medium"))
        low  = len(pet.get_tasks_by_priority("low"))
        st.markdown(
            f"- **{pet.name}** ({pet.species}, {pet.age_years} yr) — "
            f"{len(pet.tasks)} task(s): "
            f"{PRIORITY_BADGE['high']} ×{high}  {PRIORITY_BADGE['medium']} ×{med}  {PRIORITY_BADGE['low']} ×{low}"
        )
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3 — Add a care task
# ---------------------------------------------------------------------------

st.divider()
st.header("3. Add a Care Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        with col2:
            task_category = st.selectbox(
                "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "general"]
            )
        col3, col4, col5 = st.columns(3)
        with col3:
            task_title = st.text_input("Task title", value="Morning walk")
        with col4:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col5:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=task_category,
        )
        target_pet.add_task(new_task)
        st.session_state.last_plan = []   # invalidate cached plan
        st.success(
            f"Added **{task_title}** ({PRIORITY_BADGE[priority]}, {duration} min) "
            f"to {target_pet_name}."
        )

    # Task list sorted by urgency_score descending — mirrors scheduler order
    for pet in owner.pets:
        if not pet.tasks:
            continue
        st.subheader(f"{CATEGORY_ICON.get('general', '📋')} {pet.name}'s tasks (sorted by priority)")
        sorted_tasks = sorted(pet.tasks, key=lambda t: t.urgency_score(), reverse=True)
        rows = [
            {
                "Icon": CATEGORY_ICON.get(t.category, "📋"),
                "Title": t.title,
                "Category": t.category,
                "Duration (min)": t.duration_minutes,
                "Priority": PRIORITY_BADGE[t.priority],
                "Done": "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ]
        st.table(rows)

    # Budget overview whenever tasks exist
    if owner.total_task_minutes() > 0:
        st.subheader("Time budget overview")
        _budget_bar(owner)

# ---------------------------------------------------------------------------
# Section 4 — Generate the daily schedule
# ---------------------------------------------------------------------------

st.divider()
st.header("4. Generate Today's Schedule")

all_tasks_count = sum(len(p.tasks) for p in owner.pets)

if all_tasks_count == 0:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule", type="primary"):
        scheduler = Scheduler(owner=owner, day_start_minute=8 * 60)
        plan = scheduler.build_full_plan()
        st.session_state.last_plan = plan

    plan = st.session_state.last_plan

    if plan:
        scheduled_min = sum(s.task.duration_minutes for s in plan)
        st.success(
            f"Scheduled **{len(plan)} task(s)** using **{scheduled_min} of "
            f"{owner.available_minutes} min** available."
        )

        # ── Priority summary strip ──────────────────────────────────────────
        high_ct  = sum(1 for s in plan if s.task.priority == "high")
        med_ct   = sum(1 for s in plan if s.task.priority == "medium")
        low_ct   = sum(1 for s in plan if s.task.priority == "low")
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 High-priority tasks", high_ct)
        c2.metric("🟡 Medium-priority tasks", med_ct)
        c3.metric("🟢 Low-priority tasks", low_ct)

        # ── Timeline ───────────────────────────────────────────────────────
        st.subheader("Today's Plan")
        for item in plan:
            icon = CATEGORY_ICON.get(item.task.category, "📋")
            badge = PRIORITY_BADGE[item.task.priority]
            done_icon = "✅" if item.task.completed else "🔲"
            st.markdown(
                f"{done_icon} **{item.time_label()}**  ·  {icon} "
                f"*{item.pet_name}*: **{item.task.title}**  "
                f"· {badge} · {item.task.duration_minutes} min"
            )
            with st.expander("Why was this task scheduled?"):
                st.write(item.reason)

        # ── Full text explanation ───────────────────────────────────────────
        with st.expander("Full plain-text plan"):
            scheduler_obj = Scheduler(owner=owner, day_start_minute=8 * 60)
            st.code(scheduler_obj.explain_plan(plan))

        # ── Conflict / skipped-task warning ────────────────────────────────
        scheduled_ids = {id(s.task) for s in plan}
        skipped = [
            (p.name, t)
            for p in owner.pets
            for t in p.tasks
            if id(t) not in scheduled_ids
        ]
        if skipped:
            st.warning("⚠️ **Tasks not scheduled** (didn't fit in today's time budget):")
            for pet_name, task in skipped:
                st.markdown(
                    f"- **{pet_name}**: {task.title} "
                    f"({PRIORITY_BADGE[task.priority]}, {task.duration_minutes} min)  \n"
                    f"  *Tip: raise your time budget or lower-priority tasks to make room.*"
                )
        else:
            st.success("All tasks fit within today's time budget!")
