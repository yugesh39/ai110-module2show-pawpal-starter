import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# --- "Memory" setup ---------------------------------------------------
# st.session_state is the "vault" that survives Streamlit's top-to-bottom
# reruns. We only create the Owner/Pet the first time; every later rerun
# reuses the same instances instead of recreating empty ones.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name=owner_name,
        available_start="07:00",
        available_end="21:00",
    )

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species)
    # UI action -> Phase 2 logic: Owner.add_pet()
    st.session_state.owner.add_pet(st.session_state.pet)

owner = st.session_state.owner
pet = st.session_state.pet

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(
        name=task_title,
        duration_minutes=int(duration),
        priority=priority,
    )
    # UI action -> Phase 2 logic: Pet.add_task()
    pet.add_task(new_task)

if pet.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {"name": t.name, "duration_minutes": t.duration_minutes, "priority": t.priority}
            for t in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a plan using Scheduler.generate_plan() from pawpal_system.py.")

if st.button("Generate schedule"):
    if not pet.tasks:
        st.info("Add at least one task before generating a schedule.")
    else:
        # UI action -> Phase 2 logic: Scheduler.generate_plan()
        scheduler = Scheduler(owner, pet)
        plan = scheduler.generate_plan()

        if plan["schedule"]:
            st.write("### 📅 Today's Plan")
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

        with st.expander("Scheduler reasoning log"):
            for line in plan["log"]:
                st.write(f"- {line}")