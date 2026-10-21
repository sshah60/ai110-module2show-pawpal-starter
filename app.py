"""Streamlit interface. All scheduling rules live in pawpal_system.py."""
from datetime import date, datetime
import os
from pathlib import Path
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.markdown("Plan care for every pet, track completion, and spot scheduling conflicts.")
st.caption("Use Save data to keep pets and tasks between runs.")
data_path = Path(os.environ.get("PAWPAL_DATA_FILE", str(Path(__file__).with_name("data.json"))))

if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json(data_path) if data_path.exists() else Owner("Jordan")
    except (ValueError, OSError) as error:
        st.error(f"Could not load saved data: {error}. The file has not been changed.")
        st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)
with st.expander("Saved data"):
    st.caption("Save after making changes. Saved data loads automatically on the next run.")
    if st.button("Save data"):
        try:
            owner.save_to_json(data_path)
            st.success("Pets and tasks saved to data.json.")
        except OSError as error:
            st.error(f"Could not save: {error}")


with st.expander("Owner and preferences", expanded=True):
    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value=owner.name)
        preferences = st.text_input("Preferences (notes)", value=owner.preferences)
        if st.form_submit_button("Save owner"):
            if owner_name.strip():
                owner.name = owner_name.strip()
                owner.preferences = preferences.strip()
                st.success("Owner saved.")
            else:
                st.error("Owner name is required.")

st.subheader("Add a pet")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        try:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name.strip()}.")
        except ValueError as error:
            st.error(str(error))

if not owner.pets:
    st.info("Add a pet to start planning care.")
    st.stop()
st.write("Pets: " + ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets))

st.subheader("Tasks")
with st.form("task_form", clear_on_submit=True):
    selected_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])
    selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)
    task_title = st.text_input("Task title")
    due_date = st.date_input("Due date", value=date.today())
    task_time = st.time_input("Time", value=datetime.strptime("08:00", "%H:%M").time())
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    if st.form_submit_button("Add task"):
        try:
            selected_pet.add_task(Task(task_title.strip(), task_time.strftime("%H:%M"),
                                      due_date, int(duration), priority, frequency))
            st.success("Task added.")
        except ValueError as error:
            st.error(str(error))

pending = scheduler.filter_tasks(completed=False)
if pending:
    with st.expander("Edit or complete a task"):
        labels = {task.task_id: f"{pet.name}: {task.title} ({task.due_date} {task.time})"
                  for pet, task in pending}
        selected_id = st.selectbox("Choose pending task", list(labels), format_func=labels.get)
        pet, task = next((pet, task) for pet, task in pending if task.task_id == selected_id)
        # A task-specific form key keeps edits from leaking between task selections.
        with st.form(f"edit_{task.task_id}"):
            edited_title = st.text_input("Edit title", value=task.title)
            edited_date = st.date_input("Edit date", value=task.due_date)
            edited_time = st.time_input("Edit time", value=datetime.strptime(task.time, "%H:%M").time())
            edited_duration = st.number_input("Edit duration", min_value=1, max_value=240, value=task.duration_minutes)
            edited_priority = st.selectbox("Edit priority", ["low", "medium", "high"], index=["low", "medium", "high"].index(task.priority))
            edited_frequency = st.selectbox("Edit frequency", ["once", "daily", "weekly"], index=["once", "daily", "weekly"].index(task.frequency))
            if st.form_submit_button("Save task changes"):
                try:
                    scheduler.update_task(pet, task, title=edited_title.strip(), due_date=edited_date,
                                          time=edited_time.strftime("%H:%M"), duration_minutes=int(edited_duration),
                                          priority=edited_priority, frequency=edited_frequency)
                    st.session_state.notice = "Task updated."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
        if st.button("Mark task complete"):
            following = scheduler.mark_task_complete(pet, task)
            st.session_state.notice = "Task completed." + (f" Next occurrence: {following.due_date}." if following else "")
            st.rerun()

if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))

left, middle, right = st.columns(3)
left.metric("Pets", len(owner.pets))
middle.metric("Pending tasks", len(scheduler.filter_tasks(completed=False)))
right.metric("Completed tasks", len(scheduler.filter_tasks(completed=True)))

st.divider()
st.subheader("Build Schedule")
view_day = st.date_input("Schedule date", value=date.today())
pet_filter = st.selectbox("Filter by pet", ["All pets"] + [pet.name for pet in owner.pets])
status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
budget = st.number_input("Available care minutes", min_value=0, max_value=1440, value=60)
name_filter = None if pet_filter == "All pets" else pet_filter
completed_filter = {"All": None, "Pending": False, "Completed": True}[status]

rows = scheduler.sort_by_time(scheduler.filter_tasks(name_filter, completed_filter, view_day))
if rows:
    st.table([{"Pet": pet.name, "Task": task.title, "Date": str(task.due_date), "Time": task.time,
               "Minutes": task.duration_minutes, "Priority": task.priority,
               "Frequency": task.frequency, "Status": "✅ Complete" if task.completed else "🕒 Pending"} for pet, task in rows])
else:
    st.info("No tasks match these filters.")

# Check every pet for this day, even when the table displays only one pet.
for warning in scheduler.detect_conflicts(scheduler.filter_tasks(day=view_day, completed=False)):
    st.warning(warning)
st.caption("Warnings flag identical start times, including tasks for different pets. Times are not moved automatically.")

if st.button("Generate schedule"):
    chosen, skipped = scheduler.build_schedule(view_day, int(budget), name_filter)
    st.session_state.show_schedule = True
if st.session_state.get("show_schedule", False):
    # Recompute after edits or completion so the displayed plan never becomes stale.
    chosen, skipped = scheduler.build_schedule(view_day, int(budget), name_filter)
    st.markdown("### Daily plan")
    st.caption("Pending tasks only. High priorities are chosen first, then the plan is ordered by time. Preferences are notes.")
    if chosen:
        st.table([{"Time": task.time, "Pet": pet.name, "Task": task.title, "Why": reason}
                  for pet, task, reason in chosen])
    else:
        st.info("No pending task fits this day and budget.")
    for pet, task in skipped:
        st.info(f"Skipped {pet.name}: {task.title} — does not fit the remaining care-minute budget.")


with st.expander("Find the next available slot"):
    st.caption("Checks task durations across every pet. Completed tasks do not block time.")
    slot_day = st.date_input("Slot date", value=date.today())
    slot_duration = st.number_input("Slot duration (minutes)", min_value=1, max_value=1440, value=20)
    slot_start = st.time_input("Start searching at", value=datetime.strptime("08:00", "%H:%M").time())
    if st.button("Find free slot"):
        result = scheduler.next_available_slot(slot_day, int(slot_duration), slot_start.strftime("%H:%M"))
        if result is None:
            st.warning("No free slot of that length remains on this day.")
        else:
            st.success(f"Next available slot: {slot_day} at {result} for {int(slot_duration)} minutes.")
