import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add one or more pets, give them tasks (with an optional time and
recurrence), and PawPal+ will sort, filter, flag conflicts, and build a daily plan for you.
"""
)

# --- "Memory" setup ---------------------------------------------------
# st.session_state is the "vault" that survives Streamlit's top-to-bottom
# reruns. We only create the Owner once; every later rerun reuses the
# same instance instead of recreating an empty one.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_start="07:00",
        available_end="21:00",
    )

owner = st.session_state.owner

st.divider()

# ---------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------
st.subheader("🐶 Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted and new_pet_name:
    owner.add_pet(Pet(name=new_pet_name, species=new_pet_species))
    st.success(f"Added {new_pet_name} ({new_pet_species}).")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

pet_names = [p.name for p in owner.pets]
st.caption(f"Current pets: {', '.join(pet_names)}")

st.divider()

# ---------------------------------------------------------------------
# Add a task to a chosen pet
# ---------------------------------------------------------------------
st.subheader("📝 Add a Task")

with st.form("add_task_form", clear_on_submit=True):
    target_pet_name = st.selectbox("For which pet?", pet_names)

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=0, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"], index=2)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"], index=0)

    has_time = st.checkbox("Pin to a specific time?")
    preferred_time = None
    if has_time:
        t = st.time_input("Preferred time", value=None)
        if t is not None:
            preferred_time = t.strftime("%H:%M")

    add_task_submitted = st.form_submit_button("Add task")

if add_task_submitted and task_title:
    target_pet = next(p for p in owner.pets if p.name == target_pet_name)
    target_pet.add_task(
        Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            preferred_time=preferred_time,
        )
    )
    st.success(f"Added '{task_title}' for {target_pet_name}.")

st.divider()

# ---------------------------------------------------------------------
# View tasks: sorting + filtering, powered by Scheduler
# ---------------------------------------------------------------------
st.subheader("📋 All Tasks")

# The Scheduler needs a "primary" pet for generate_plan(), but sort_by_time,
# filter_tasks, detect_conflicts, and mark_task_complete all work across
# every pet the owner has -- so any pet works as the anchor here.
scheduler = Scheduler(owner, owner.pets[0])

col1, col2, col3 = st.columns(3)
with col1:
    sort_mode = st.radio("Sort by", ["Time", "Priority (default order)"], horizontal=False)
with col2:
    status_filter = st.selectbox("Status", ["All", "Incomplete only", "Completed only"])
with col3:
    pet_filter = st.selectbox("Pet", ["All pets"] + pet_names)

# Build the view using Scheduler.filter_tasks() first...
filter_kwargs = {}
if status_filter == "Incomplete only":
    filter_kwargs["completed"] = False
elif status_filter == "Completed only":
    filter_kwargs["completed"] = True
if pet_filter != "All pets":
    filter_kwargs["pet_name"] = pet_filter

visible_tasks = scheduler.filter_tasks(**filter_kwargs)

# ...then Scheduler.sort_by_time() on top of that, if the user asked for it.
if sort_mode == "Time":
    visible_tasks = scheduler.sort_by_time(visible_tasks)

if visible_tasks:
    # A plain st.table can't hold a per-row button, so each task gets its
    # own row of columns with a "Mark complete" button next to it.
    for task in visible_tasks:
        owning_pet = next(p for p in owner.pets if task in p.tasks)
        c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 2])
        c1.write(f"**{owning_pet.name}**")
        c2.write(task.name)
        c3.write(task.preferred_time or "—")
        c4.write(f"{task.priority}" + (f" · {task.frequency}" if task.frequency != "once" else ""))
        if task.completed:
            c5.write("✅ done")
        else:
            if c5.button("Mark complete", key=f"complete_{task.id}"):
                # Scheduler.mark_task_complete searches all pets and, for
                # daily/weekly tasks, automatically spawns the next occurrence.
                scheduler.mark_task_complete(task.id)
                st.rerun()
else:
    st.info("No tasks match the current filters.")

st.divider()

# ---------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------
st.subheader("⚠️ Conflict Check")

conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No scheduling conflicts detected.")

st.divider()

# ---------------------------------------------------------------------
# Build Schedule (per pet, since generate_plan works on one pet's day)
# ---------------------------------------------------------------------
st.subheader("📅 Build Schedule")

schedule_pet_name = st.selectbox("Generate a plan for which pet?", pet_names, key="schedule_pet")

if st.button("Generate schedule"):
    schedule_pet = next(p for p in owner.pets if p.name == schedule_pet_name)
    if not schedule_pet.tasks:
        st.info(f"{schedule_pet_name} has no tasks yet. Add one above.")
    else:
        plan_scheduler = Scheduler(owner, schedule_pet)
        plan = plan_scheduler.generate_plan()

        if plan["schedule"]:
            st.success(f"Built a plan with {len(plan['schedule'])} task(s) for {schedule_pet_name}.")
            st.table(
                [
                    {
                        "task": item["task"].name,
                        "start": item["start"],
                        "end": item["end"],
                        "priority": item["task"].priority,
                    }
                    for item in plan["schedule"]
                ]
            )
        else:
            st.warning("No tasks could be scheduled in the available time window.")

        if plan["skipped"]:
            st.write("### ⏭️ Skipped Tasks")
            st.table([{"task": t.name, "priority": t.priority} for t in plan["skipped"]])

        if plan["conflicts"]:
            st.write("### ⚠️ Conflicts in this plan")
            for warning in plan["conflicts"]:
                st.warning(warning)

        with st.expander("Scheduler reasoning log"):
            for line in plan["log"]:
                st.write(f"- {line}")