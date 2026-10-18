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

# ------------------------------------------------------------ Task list
st.subheader("All Tasks")
all_tasks = owner.get_all_tasks()
if all_tasks:
    st.table(
        [
            {
                "Pet": task.pet_name,
                "Date": task.due_date.isoformat(),
                "Time": task.time,
                "Description": task.description,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Status": "Done" if task.completed else "Pending",
            }
            for task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")
