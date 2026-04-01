import streamlit as st
from datetime import date
from pawpal_system import Pet, CareTask, Owner, DailyPlan, Scheduler
from ai_advisor import run_ai_advisor

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("PawPal+")

# --- Session state initialisation ---
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []   # list of CareTask objects

if "plan" not in st.session_state:
    st.session_state.plan = None

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

# --- Owner & Pet setup ---
st.subheader("Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")

col1, col2, col3, col4 = st.columns(4)
with col1:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col2:
    breed = st.text_input("Breed", value="Mixed")
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
with col4:
    weight = st.number_input("Weight (kg)", min_value=0.1, max_value=100.0, value=10.0)

availability_input = st.text_input(
    "Available time slots (comma-separated, e.g. 07:00-09:00, 17:00-20:00)",
    value="07:00-09:00, 17:00-20:00",
)

if st.button("Save Owner & Pet"):
    slots = [s.strip() for s in availability_input.split(",") if s.strip()]
    pet = Pet(name=pet_name, species=species, breed=breed, age=int(age), weight=float(weight))
    owner = Owner(name=owner_name, available_time_slots=slots)
    owner.add_pet(pet)
    st.session_state.pet = pet
    st.session_state.owner = owner
    st.session_state.tasks = []
    st.session_state.plan = None
    st.success(f"Saved {owner_name} with pet {pet_name} ({species}, age {int(age)}). Availability: {', '.join(slots)}")
    # Notify about auto-generated tasks triggered by the pet's profile
    auto_task_names = []
    if species == "dog" and 0 < int(age) < 2:
        auto_task_names.append("daily Training Session (puppy rule)")
    if species == "cat" and int(age) >= 10:
        auto_task_names.append("weekly Weight Check (senior cat rule)")
    if auto_task_names:
        st.info(f"Profile rules will auto-add for {pet_name}: {', '.join(auto_task_names)}")

# --- Task entry ---
st.divider()
st.subheader("Tasks")

if st.session_state.pet is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_type = st.selectbox(
            "Type", ["walk", "feed", "medication", "grooming", "enrichment", "training"],
            help="'medication' gets a priority bonus during scheduling"
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority (1=low, 5=critical)", [1, 2, 3, 4, 5], index=2)
    with col3:
        frequency = st.selectbox(
            "Frequency", ["daily", "twice_daily", "weekly"],
            help="'twice_daily' splits into AM and PM instances"
        )

    time_window_am = ""
    time_window_pm = ""
    if frequency == "twice_daily":
        st.info("twice_daily tasks need two time windows so AM and PM instances land in separate parts of the day.")
        col1, col2 = st.columns(2)
        with col1:
            time_window_am = st.text_input("AM window (e.g. 07:00-09:00)", value="07:00-09:00")
        with col2:
            time_window_pm = st.text_input("PM window (e.g. 17:00-19:00)", value="17:00-19:00")

    if st.button("Add task"):
        preferred_windows = []
        if frequency == "twice_daily":
            if time_window_am and time_window_pm:
                preferred_windows = [time_window_am.strip(), time_window_pm.strip()]
            else:
                st.warning("Please enter both an AM and PM time window for twice_daily tasks.")
                st.stop()
        task = CareTask(
            task_type=task_type,
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            preferred_time_windows=preferred_windows,
        )
        st.session_state.pet.add_care_task(task)
        st.session_state.tasks.append(task)
        st.success(f"Added task: {task_title}")

    if st.session_state.tasks:
        st.write("Current tasks:")
        st.table([
            {
                "Task": t.name,
                "Type": t.task_type,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency,
            }
            for t in st.session_state.tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

# --- AI Care Advisor ---
st.divider()
st.subheader("AI Care Advisor")

if st.session_state.pet is None:
    st.info("Save an owner and pet above to use the AI advisor.")
else:
    pet = st.session_state.pet
    st.write(
        f"Claude will analyse **{pet.name}'s** profile and retrieve relevant care guidelines "
        "from the knowledge base to suggest a personalised task list."
    )

    if st.button("Generate AI Care Plan", type="primary"):
        st.session_state.ai_result = None
        existing_names = [t.name for t in st.session_state.tasks]
        with st.spinner(f"Analysing {pet.name}'s needs and retrieving care guidelines…"):
            result = run_ai_advisor(pet, existing_names)
        st.session_state.ai_result = result

    if st.session_state.ai_result is not None:
        result = st.session_state.ai_result

        if result["error"]:
            st.error(result["error"])
        else:
            if result["explanation"]:
                with st.expander("AI Reasoning", expanded=True):
                    st.write(result["explanation"])

            pending = [
                t for t in result["tasks"]
                if t.name not in [x.name for x in st.session_state.tasks]
            ]

            if pending:
                st.markdown(f"**{len(pending)} task(s) suggested — review and add:**")
                h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 1.5, 1, 1.5, 1.5])
                for label, col in zip(
                    ["Task", "Type", "Duration", "Pri.", "Frequency", ""],
                    [h1, h2, h3, h4, h5, h6],
                ):
                    col.markdown(f"**{label}**")
                st.divider()

                for i, task in enumerate(pending):
                    c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 1.5, 1, 1.5, 1.5])
                    c1.write(task.name)
                    c2.write(task.task_type)
                    c3.write(f"{task.duration_minutes} min")
                    c4.write(str(task.priority))
                    c5.write(task.frequency)
                    if c6.button("Add", key=f"ai_add_{i}_{task.name}"):
                        st.session_state.pet.add_care_task(task)
                        st.session_state.tasks.append(task)
                        st.session_state.plan = None
                        st.rerun()

                if st.button("Add all suggested tasks"):
                    added = 0
                    for task in pending:
                        if task.name not in [t.name for t in st.session_state.tasks]:
                            st.session_state.pet.add_care_task(task)
                            st.session_state.tasks.append(task)
                            added += 1
                    st.session_state.ai_result = None
                    st.session_state.plan = None
                    st.success(f"Added {added} task(s). Generate the schedule below to see the plan.")
                    st.rerun()
            else:
                st.success(
                    "No new tasks to add — the existing task list already covers "
                    f"{pet.name}'s care needs."
                )

# --- Schedule generation ---
st.divider()
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an owner and pet first.")
    elif not st.session_state.tasks:
        st.warning("Please add at least one task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        st.session_state.plan = scheduler.generate_daily_plan(date.today())
        st.success("Schedule generated!")

if st.session_state.plan is not None:
    plan = st.session_state.plan

    # --- Summary metrics ---
    st.markdown(f"### {plan.date.strftime('%A, %B %d, %Y')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tasks scheduled", len(plan.scheduled_tasks))
    with col2:
        st.metric("Total time", f"{plan.total_duration_minutes} min")
    with col3:
        st.metric("Could not fit", len(plan.unscheduled_tasks))

    # --- Conflict detection (Scheduler.detect_conflicts) ---
    conflicts = Scheduler(st.session_state.owner).detect_conflicts(plan)
    if conflicts:
        for report in conflicts:
            st.warning(str(report))
    else:
        st.success("No scheduling conflicts detected.")

    # --- Scheduled tasks (sorted chronologically by Scheduler.sort_by_time) ---
    if plan.scheduled_tasks:
        st.markdown("**Scheduled tasks** — sorted chronologically:")
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 3, 1.5, 1, 2, 2])
        for header, col in zip(["Time", "Task", "Duration", "Pri.", "Status", ""], [h1, h2, h3, h4, h5, h6]):
            col.markdown(f"**{header}**")
        st.divider()
        for time_str, t in plan.scheduled_tasks:
            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 3, 1.5, 1, 2, 2])
            c1.write(time_str)
            c2.write(t.name)
            c3.write(f"{t.duration_minutes} min")
            c4.write(str(t.priority))
            if t.is_completed:
                c5.success("Done")
                c6.write("—")
            else:
                c5.write("Pending")
                if c6.button("Mark done", key=f"done_{t.name}_{time_str}"):
                    t.mark_complete(on_date=plan.date)
                    st.rerun()
    else:
        st.warning("No tasks could be scheduled. Check that your availability slots are set correctly.")

    # --- Tasks that didn't fit ---
    if plan.unscheduled_tasks:
        st.warning(
            f"{len(plan.unscheduled_tasks)} task(s) could not fit into your available slots:"
        )
        st.table([
            {
                "Task": t.name,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
            }
            for t in plan.unscheduled_tasks
        ])

    # --- Reasoning (collapsed by default) ---
    with st.expander("Scheduling reasoning"):
        st.write(plan.reasoning)
