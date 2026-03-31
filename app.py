"""
app.py — PawPal+ Streamlit UI.

Connects the Owner / Pet / Task / Scheduler logic layer to an interactive UI.
st.session_state acts as the persistent "vault" that survives page reruns.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler  # Step 1: import logic layer

# ---------------------------------------------------------------------------
# Step 2: Initialise session state — only runs the very first time
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None          # set after the owner form is submitted

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
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
    # Preserve existing pets if the owner is being updated
    existing_pets = st.session_state.owner.pets if st.session_state.owner else []
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    for pet in existing_pets:
        st.session_state.owner.add_pet(pet)
    st.success(f"Owner saved: {owner_name} ({available_minutes} min available today)")

if st.session_state.owner:
    o = st.session_state.owner
    st.info(f"Current owner: **{o.name}** — {o.available_minutes} min budget — {len(o.pets)} pet(s) registered")
else:
    st.warning("Fill in your name above and click **Save owner** to get started.")
    st.stop()   # nothing below makes sense without an owner

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
    # Step 3: wire the form to Owner.add_pet()
    new_pet = Pet(name=pet_name, species=species, age_years=int(age_years))
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}!")

# Show registered pets
owner: Owner = st.session_state.owner
if owner.pets:
    st.subheader("Registered pets")
    for pet in owner.pets:
        st.markdown(f"- **{pet.name}** ({pet.species}, {pet.age_years} yr) — {len(pet.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3 — Add a task to a pet
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
        # Step 3: wire to Pet.add_task()
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=task_category,
        )
        target_pet.add_task(new_task)
        st.success(f"Added '{task_title}' ({priority} priority, {duration} min) to {target_pet_name}.")

    # Show all tasks grouped by pet
    for pet in owner.pets:
        if pet.tasks:
            st.subheader(f"{pet.name}'s tasks")
            rows = [
                {
                    "Title": t.title,
                    "Category": t.category,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Done": "✓" if t.completed else "",
                }
                for t in pet.tasks
            ]
            st.table(rows)

# ---------------------------------------------------------------------------
# Section 4 — Generate the daily schedule
# ---------------------------------------------------------------------------

st.divider()
st.header("4. Generate Today's Schedule")

all_tasks_count = sum(len(p.tasks) for p in owner.pets)
total_task_min = owner.total_task_minutes()

col_a, col_b = st.columns(2)
col_a.metric("Total task time", f"{total_task_min} min")
col_b.metric("Time budget", f"{owner.available_minutes} min")

if all_tasks_count == 0:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule", type="primary"):
        scheduler = Scheduler(owner=owner, day_start_minute=8 * 60)  # starts at 8:00 AM
        plan = scheduler.build_full_plan()

        if plan:
            st.success(f"Scheduled {len(plan)} task(s) across your pets.")
            st.subheader("Today's Plan")
            for st_task in plan:
                done_icon = "✅" if st_task.task.completed else "🔲"
                st.markdown(
                    f"{done_icon} **{st_task.time_label()}** — "
                    f"*{st_task.pet_name}*: {st_task.task.title} "
                    f"({st_task.task.duration_minutes} min, {st_task.task.priority} priority)"
                )
                with st.expander("Why this task?"):
                    st.write(st_task.reason)

            # Full text explanation
            with st.expander("Full plan explanation"):
                scheduler_obj = Scheduler(owner=owner, day_start_minute=8 * 60)
                st.code(scheduler_obj.explain_plan(plan))

            # Warn about unscheduled tasks
            scheduled_titles = {st_t.task.title for st_t in plan}
            skipped = [
                f"{p.name}: {t.title}"
                for p in owner.pets
                for t in p.tasks
                if t.title not in scheduled_titles
            ]
            if skipped:
                st.warning(
                    "The following tasks didn't fit in today's time budget:\n"
                    + "\n".join(f"- {s}" for s in skipped)
                )
        else:
            st.error("No tasks could be scheduled. Check that tasks fit within your time budget.")
