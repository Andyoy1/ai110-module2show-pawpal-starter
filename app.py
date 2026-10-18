from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planner: add your pets, then schedule their care tasks.")

# Create the owner (and scheduler) once; they survive every rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner = st.session_state.owner

# ---------------------------------------------------------------- Owner
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name).strip() or owner.name

# ----------------------------------------------------------------- Pets
st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    try:
        owner.add_pet(Pet(new_pet_name.strip(), new_pet_species))
        st.success(f"Added {new_pet_name.strip()} the {new_pet_species}.")
    except ValueError as error:
        st.error(str(error))

if owner.pets:
    st.table([{"Pet": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("No pets yet. Add your first pet above.")

# ---------------------------------------------------------------- Tasks
st.subheader("Add a Care Task")
if not owner.pets:
    st.info("Add a pet before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [pet.name for pet in owner.pets])
        description = st.text_input("Description", placeholder="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due date", value=date.today())
        with col2:
            due_time = st.time_input("Time", value=None, step=300)
        col3, col4, col5 = st.columns(3)
        with col3:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col4:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col5:
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        if not description.strip():
            st.error("Please enter a task description.")
        elif due_time is None:
            st.error("Please choose a time.")
        else:
            # Find the pet by its exact stored name.
            pet = next(p for p in owner.pets if p.name == pet_choice)
            task = Task(
                description=description.strip(),
                pet_name=pet.name,
                due_date=due_date,
                time=due_time.strftime("%H:%M"),
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
            )
            try:
                pet.add_task(task)
                st.success(f"Added '{task.description}' for {pet.name}.")
            except ValueError as error:
                st.error(str(error))

# ------------------------------------------------------------- Schedule
st.subheader("Schedule")
st.caption(
    "Tasks appear by date and time, with higher priority first when times match. "
    "Conflicts only trigger a warning; tasks are never moved."
)
scheduler = st.session_state.scheduler

col_date, col_pet, col_status = st.columns(3)
with col_date:
    view_date = st.date_input("Date", value=date.today(), key="view_date")
with col_pet:
    pet_filter = st.selectbox(
        "Pet", ["All pets"] + [pet.name for pet in owner.pets], key="pet_filter"
    )
with col_status:
    status_filter = st.selectbox(
        "Status", ["All", "Incomplete", "Completed"], key="status_filter"
    )

# The message from the last completion survives the rerun that follows it.
if "completion_message" in st.session_state:
    st.success(st.session_state.completion_message)

# Conflicts look at every pet on the selected date, ignoring the display filters.
for warning in scheduler.detect_conflicts(scheduler.filter_tasks(due_date=view_date)):
    st.warning(f"Scheduling conflict (all pets, {view_date}): {warning}")

shown = scheduler.sort_by_time(
    scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Incomplete": False, "Completed": True}[status_filter],
        due_date=view_date,
    )
)

if shown:
    st.table(
        [
            {
                "Time": task.time,
                "Pet": task.pet_name,
                "Description": task.description,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Status": "Done" if task.completed else "Pending",
            }
            for task in shown
        ]
    )
    for task in shown:
        if task.completed:
            continue
        # id(task) keeps keys unique even for identical-looking tasks.
        label = f"Complete: {task.time} {task.pet_name} - {task.description}"
        if st.button(label, key=f"complete_{id(task)}"):
            try:
                next_task = scheduler.mark_task_complete(task)
            except ValueError as error:
                st.error(str(error))
            else:
                message = f"Completed '{task.description}' for {task.pet_name}."
                if next_task is not None:
                    message += f" Next occurrence is due {next_task.due_date}."
                st.session_state.completion_message = message
                st.rerun()
else:
    st.info("No tasks match these filters for the selected date.")
