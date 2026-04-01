"""
PawPal+ Pet Care Planning System
Class definitions for pet care task management and scheduling.
"""

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_time_window(window: str) -> tuple[int, int]:
    """Parse 'HH:MM-HH:MM' into (start_minute, end_minute) since midnight."""
    start_str, end_str = window.split('-')
    sh, sm = map(int, start_str.split(':'))
    eh, em = map(int, end_str.split(':'))
    return sh * 60 + sm, eh * 60 + em


def _minutes_to_time_str(minutes: int) -> str:
    """Convert minutes since midnight to 'HH:MM' string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet with care requirements."""
    name: str
    species: str
    breed: str
    age: int
    weight: float
    special_needs: list[str] = field(default_factory=list)
    medical_conditions: list[str] = field(default_factory=list)
    care_tasks: list['CareTask'] = field(default_factory=list)

    def get_care_requirements(self) -> list['CareTask']:
        """Returns all care tasks (user-defined + auto-generated) for this pet.

        Auto-generation rules:
        - Dogs under 2  → daily 15-min training session
        - Cats 10+      → weekly 5-min weight check
        - Any pet with medical_conditions → feeding tasks become time-inflexible
        """
        all_tasks = self.care_tasks.copy()

        if self.species == "dog" and 0 < self.age < 2:
            all_tasks.append(CareTask(
                task_type="training",
                name=f"{self.name}'s Training Session",
                duration_minutes=15,
                priority=3,
                frequency="daily",
                preferred_time_windows=["09:00-11:00"],
                notes="Puppy training — basic commands and socialisation",
                pet_name=self.name,
            ))

        if self.species == "cat" and self.age >= 10:
            all_tasks.append(CareTask(
                task_type="health_check",
                name=f"{self.name}'s Weight Check",
                duration_minutes=5,
                priority=2,
                frequency="weekly",
                notes="Senior cat weight monitoring",
                pet_name=self.name,
            ))

        # Pets with medical conditions need feeding on a strict schedule
        if self.medical_conditions:
            for task in all_tasks:
                if task.task_type == "feed":
                    task.is_time_flexible = False

        return all_tasks

    def add_care_task(self, task: 'CareTask') -> None:
        """Adds a care task to this pet."""
        if self.validate_task(task):
            task.pet_name = self.name
            self.care_tasks.append(task)

    def validate_task(self, task: 'CareTask') -> bool:
        """Checks if a task is appropriate for this pet."""
        return True


@dataclass
class CareTask:
    """Represents a pet care task with scheduling parameters."""
    task_type: str   # "walk", "feed", "medication", "enrichment", "grooming", …
    name: str
    duration_minutes: int
    priority: int    # 1-5, where 5 is most critical
    frequency: str   # "daily", "twice_daily", "weekly", …
    preferred_time_windows: list[str] = field(default_factory=list)  # ["08:00-09:00", …]
    notes: str = ""
    is_time_flexible: bool = True
    is_completed: bool = False
    scheduled_start_minute: Optional[int] = None  # set by Scheduler when placed
    pet_name: str = ""                      # set when the task is added to a Pet
    scheduled_weekday: Optional[int] = None  # 0=Mon…6=Sun; None = every day (weekly tasks only)
    next_due_date: Optional[date] = None    # set by mark_complete; scheduler skips task until this date

    def mark_complete(self, on_date: Optional[date] = None) -> None:
        """Marks this task complete and sets next_due_date for the next occurrence.

        daily / twice_daily → next_due_date = on_date + 1 day
        weekly              → next_due_date = on_date + 7 days
        Other frequencies   → next_due_date left unchanged.
        """
        self.is_completed = True
        completed_on = on_date or date.today()
        if self.frequency in ("daily", "twice_daily"):
            self.next_due_date = completed_on + timedelta(days=1)
        elif self.frequency == "weekly":
            self.next_due_date = completed_on + timedelta(weeks=1)

    def mark_incomplete(self) -> None:
        """Resets completion state and clears the next_due_date."""
        self.is_completed = False
        self.next_due_date = None

    def get_priority_score(self) -> float:
        """Calculates scheduling priority score.

        Base score = priority * 10  (range 10-50)
        +20 for fixed-time tasks (is_time_flexible=False)
        +15 for medication tasks
        Higher score → scheduled first.
        """
        score = float(self.priority * 10)
        if not self.is_time_flexible:
            score += 20
        if self.task_type == "medication":
            score += 15
        return score

    def conflicts_with(self, other: 'CareTask') -> bool:
        """Returns True if this task's scheduled interval overlaps with other's.

        Requires both tasks to have scheduled_start_minute set.
        """
        if self.scheduled_start_minute is None or other.scheduled_start_minute is None:
            return False
        self_end = self.scheduled_start_minute + self.duration_minutes
        other_end = other.scheduled_start_minute + other.duration_minutes
        return not (self_end <= other.scheduled_start_minute or
                    other_end <= self.scheduled_start_minute)


@dataclass
class Owner:
    """Represents the pet owner with availability and preferences."""
    name: str
    pets: list[Pet] = field(default_factory=list)
    available_time_slots: list[str] = field(default_factory=list)  # ["08:00-12:00", …]
    preferences: dict = field(default_factory=dict)
    total_available_minutes: int = 0

    def add_pet(self, pet: Pet) -> None:
        """Registers a pet under this owner."""
        self.pets.append(pet)

    def get_all_care_tasks(self) -> list[CareTask]:
        """Retrieves all care tasks for all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_care_requirements())
        return all_tasks

    def get_availability(self, target_date: date) -> list[str]:
        """Returns available time slots for a specific date.

        Weekend override: if preferences contains a 'weekend_slots' dict keyed
        by weekday number ('5' = Saturday, '6' = Sunday), those slots are used
        instead of the default available_time_slots.
        """
        weekday = target_date.weekday()  # 0 = Mon … 6 = Sun
        if weekday in (5, 6):
            weekend_slots = self.preferences.get("weekend_slots", {})
            if str(weekday) in weekend_slots:
                return weekend_slots[str(weekday)]
        return self.available_time_slots

    def is_available(self, time_str: str, duration: int) -> bool:
        """Returns True if a contiguous block [time_str, time_str+duration) falls
        entirely within one of the owner's available_time_slots."""
        h, m = map(int, time_str.split(':'))
        start = h * 60 + m
        end = start + duration
        for slot in self.available_time_slots:
            s_start, s_end = _parse_time_window(slot)
            if s_start <= start and end <= s_end:
                return True
        return False

    def set_preference(self, key: str, value) -> None:
        """Stores or updates a single owner preference by key."""
        self.preferences[key] = value


@dataclass
class DailyPlan:
    """Represents a daily schedule of pet care tasks."""
    date: date
    scheduled_tasks: list[tuple[str, CareTask]] = field(default_factory=list)
    unscheduled_tasks: list[CareTask] = field(default_factory=list)
    reasoning: str = ""
    total_duration_minutes: int = 0

    def add_task(self, task: CareTask, task_time: str) -> bool:
        """Adds task at task_time ('HH:MM') after checking for conflicts.
        Returns False (and leaves the plan unchanged) if a conflict is detected.
        """
        h, m = map(int, task_time.split(':'))
        task.scheduled_start_minute = h * 60 + m
        for _, existing in self.scheduled_tasks:
            if task.conflicts_with(existing):
                task.scheduled_start_minute = None
                return False
        self.scheduled_tasks.append((task_time, task))
        self.total_duration_minutes += task.duration_minutes
        return True

    def remove_task(self, task: CareTask) -> bool:
        """Removes a task from the schedule. Returns False if not found."""
        for i, (_, t) in enumerate(self.scheduled_tasks):
            if t is task:
                self.scheduled_tasks.pop(i)
                self.total_duration_minutes -= task.duration_minutes
                task.scheduled_start_minute = None
                return True
        return False

    def generate_explanation(self, unscheduled_reasons: Optional[dict[str, str]] = None) -> str:
        """Creates a natural language explanation for scheduling decisions.

        unscheduled_reasons: optional mapping of task name → reason string,
        produced by the Scheduler which has access to availability context.
        """
        n_scheduled = len(self.scheduled_tasks)
        n_unscheduled = len(self.unscheduled_tasks)
        parts = [
            f"Scheduled {n_scheduled} task(s) totalling {self.total_duration_minutes} min."
        ]
        if n_unscheduled:
            if unscheduled_reasons:
                task_lines = "; ".join(
                    f"{t.name} ({unscheduled_reasons.get(t.name, 'no available slot')})"
                    for t in self.unscheduled_tasks
                )
            else:
                task_lines = ", ".join(t.name for t in self.unscheduled_tasks)
            parts.append(f"{n_unscheduled} task(s) could not be fit: {task_lines}.")
        self.reasoning = " ".join(parts)
        return self.reasoning

    def get_tasks_for_pet(self, pet_name: str) -> list[tuple[str, CareTask]]:
        """Returns scheduled tasks belonging to a specific pet."""
        return [(t_str, t) for t_str, t in self.scheduled_tasks if t.pet_name == pet_name]

    def get_tasks_by_status(self, completed: bool) -> list[tuple[str, CareTask]]:
        """Returns scheduled tasks filtered by completion status."""
        return [(t_str, t) for t_str, t in self.scheduled_tasks if t.is_completed == completed]

    def filter_tasks(self, *, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> list[tuple[str, CareTask]]:
        """Returns scheduled tasks filtered by pet name, completion status, or both.

        Pass either or both keyword arguments to combine filters:
            plan.filter_tasks(pet_name="Buddy")
            plan.filter_tasks(completed=False)
            plan.filter_tasks(pet_name="Buddy", completed=False)
        """
        results = self.scheduled_tasks
        if pet_name is not None:
            results = [(t_str, t) for t_str, t in results if t.pet_name == pet_name]
        if completed is not None:
            results = [(t_str, t) for t_str, t in results if t.is_completed == completed]
        return results

    def validate_plan(self) -> tuple[bool, list[str]]:
        """Validates the plan. Returns (is_valid, list_of_issues)."""
        issues = []
        if not self.scheduled_tasks:
            issues.append("No tasks scheduled")
        # Check for overlapping tasks
        placed = [t for _, t in self.scheduled_tasks if t.scheduled_start_minute is not None]
        for i, ta in enumerate(placed):
            for tb in placed[i + 1:]:
                if ta.conflicts_with(tb):
                    issues.append(f"Conflict: '{ta.name}' overlaps '{tb.name}'")
        return (len(issues) == 0, issues)


# ---------------------------------------------------------------------------
# Conflict reporting
# ---------------------------------------------------------------------------

@dataclass
class ConflictReport:
    """Describes a scheduling overlap between two tasks.

    same_pet=True  → both tasks belong to the same pet (owner can't do both at once)
    same_pet=False → tasks belong to different pets (still a time clash)
    """
    task_a: CareTask
    task_b: CareTask
    time_a: str
    time_b: str
    same_pet: bool

    def __str__(self) -> str:
        kind = "same-pet" if self.same_pet else "cross-pet"
        pet_info = (f"both belong to {self.task_a.pet_name}"
                    if self.same_pet
                    else f"{self.task_a.pet_name or 'unknown'} vs {self.task_b.pet_name or 'unknown'}")
        return (
            f"WARNING [{kind} conflict] "
            f"'{self.task_a.name}' at {self.time_a} overlaps "
            f"'{self.task_b.name}' at {self.time_b} - {pet_info}"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Scheduling engine that generates daily plans for pet care."""

    def __init__(self, owner: Owner):
        """Binds the scheduler to an owner whose pets and availability it will read."""
        self.owner = owner

    def generate_daily_plan(self, target_date: date) -> DailyPlan:
        """Generates an optimised daily plan using a two-pass greedy algorithm.

        Algorithm
        ---------
        1. Collect all tasks from all pets (including auto-generated ones).
        2. Sort tasks by priority score descending so high-priority tasks claim
           the best slots first.
        3. Pass 1 — try to place every task inside one of its preferred time
           windows while respecting the owner's availability.
        4. Pass 2 — any task that didn't fit in pass 1 is retried with the
           window constraint relaxed: it may land anywhere in available time.
        5. Tasks that still can't fit go to unscheduled_tasks.

        Slot cursor
        -----------
        Each availability slot tracks a cursor (next free minute). When a task
        is placed at `start`, the cursor advances to `start + duration`.  Tasks
        with overlapping preferred windows that share a slot are therefore
        placed back-to-back (batching effect).

        Conflict detection
        ------------------
        Before committing a placement, conflicts_with() is checked against
        every already-scheduled task as a safety net.
        """
        all_tasks = self.owner.get_all_care_tasks()
        plan = DailyPlan(date=target_date)

        # Expand/filter tasks based on frequency before scheduling
        expanded: list[CareTask] = []
        for task in all_tasks:
            # Skip tasks that were completed and aren't due again yet
            if task.next_due_date is not None and task.next_due_date > target_date:
                continue
            if task.frequency == "weekly":
                # Skip if pinned to a weekday that doesn't match today
                if task.scheduled_weekday is not None and task.scheduled_weekday != target_date.weekday():
                    continue
                expanded.append(task)
            elif task.frequency == "twice_daily":
                windows = task.preferred_time_windows
                if len(windows) >= 2:
                    expanded.append(replace(task, name=f"{task.name} (AM)",
                                            preferred_time_windows=[windows[0]],
                                            scheduled_start_minute=None))
                    expanded.append(replace(task, name=f"{task.name} (PM)",
                                            preferred_time_windows=[windows[1]],
                                            scheduled_start_minute=None))
                else:
                    expanded.append(replace(task, name=f"{task.name} (1st)",
                                            scheduled_start_minute=None))
                    expanded.append(replace(task, name=f"{task.name} (2nd)",
                                            scheduled_start_minute=None))
            else:
                expanded.append(task)
        all_tasks = expanded

        availability = self.owner.get_availability(target_date)
        if not availability:
            plan.unscheduled_tasks = all_tasks
            plan.reasoning = "No availability configured for this date."
            return plan

        # Parse slots; cursors track the next free minute in each slot
        slots: list[tuple[int, int]] = [_parse_time_window(s) for s in availability]
        cursors: list[int] = [start for start, _ in slots]

        committed: list[tuple[str, CareTask]] = []  # (time_str, task) pairs

        def _try_place(task: CareTask, relax_window: bool) -> bool:
            """Attempt to place task into the earliest fitting availability slot.

            When relax_window=False the task must land inside one of its
            preferred_time_windows.  When relax_window=True that constraint is
            dropped and the task may start anywhere the cursor allows.

            On success: sets task.scheduled_start_minute, appends to committed,
            advances the slot cursor, and returns True.
            On failure: leaves task.scheduled_start_minute as None and returns False.
            """
            task_windows = None
            if task.preferred_time_windows and not relax_window:
                task_windows = [_parse_time_window(w) for w in task.preferred_time_windows]

            for i, (_, slot_end) in enumerate(slots):
                cursor = cursors[i]

                if task_windows:
                    # Find the earliest position that satisfies any preferred window
                    placed_start = None
                    for tw_start, tw_end in task_windows:
                        effective_start = max(cursor, tw_start)
                        effective_end = min(slot_end, tw_end)
                        if effective_end - effective_start >= task.duration_minutes:
                            placed_start = effective_start
                            break
                    if placed_start is None:
                        continue
                else:
                    # Flexible placement: use cursor if there's enough room
                    if cursor + task.duration_minutes > slot_end:
                        continue
                    placed_start = cursor

                # Conflict check against already-committed tasks
                task.scheduled_start_minute = placed_start
                if any(task.conflicts_with(t) for _, t in committed):
                    task.scheduled_start_minute = None
                    continue

                # Commit the placement
                time_str = _minutes_to_time_str(placed_start)
                committed.append((time_str, task))
                cursors[i] = placed_start + task.duration_minutes
                return True

            task.scheduled_start_minute = None
            return False

        # Sort by priority score descending; same-priority tasks keep insertion order
        sorted_tasks = sorted(all_tasks, key=lambda t: t.get_priority_score(), reverse=True)

        # Pass 1: respect preferred time windows
        needs_retry: list[CareTask] = []
        for task in sorted_tasks:
            if not _try_place(task, relax_window=False):
                needs_retry.append(task)

        # Pass 2: relax window constraint for tasks that didn't fit
        unscheduled: list[CareTask] = []
        for task in needs_retry:
            if not _try_place(task, relax_window=True):
                unscheduled.append(task)

        # Diagnose why each unscheduled task couldn't be placed
        total_available = sum(e - s for s, e in slots)
        unscheduled_reasons: dict[str, str] = {}
        for task in unscheduled:
            if task.duration_minutes > total_available:
                reason = f"task is {task.duration_minutes} min but only {total_available} min available total"
            elif task.preferred_time_windows:
                # Check whether any preferred window overlaps any availability slot
                task_windows = [_parse_time_window(w) for w in task.preferred_time_windows]
                has_overlap = any(
                    min(slot_end, tw_end) - max(slot_start, tw_start) >= task.duration_minutes
                    for slot_start, slot_end in slots
                    for tw_start, tw_end in task_windows
                )
                if has_overlap:
                    reason = "preferred window exists but slot already full"
                else:
                    reason = (
                        f"preferred window ({', '.join(task.preferred_time_windows)}) "
                        "does not overlap available slots"
                    )
            else:
                reason = "not enough contiguous time left in available slots"
            unscheduled_reasons[task.name] = reason

        # Finalise plan
        committed = Scheduler.sort_by_time(committed)
        plan.scheduled_tasks = committed
        plan.unscheduled_tasks = unscheduled
        plan.total_duration_minutes = sum(t.duration_minutes for _, t in committed)
        plan.generate_explanation(unscheduled_reasons)

        return plan

    def detect_conflicts(self, plan: DailyPlan) -> list[ConflictReport]:
        """Scans a DailyPlan for overlapping tasks and returns ConflictReport warnings.

        Lightweight and non-crashing: always returns a list (empty = no conflicts).
        Each ConflictReport classifies the overlap as same-pet or cross-pet and
        can be printed directly as a human-readable warning string.
        """
        reports: list[ConflictReport] = []
        placed = [
            (t_str, t) for t_str, t in plan.scheduled_tasks
            if t.scheduled_start_minute is not None
        ]
        for i, (time_a, task_a) in enumerate(placed):
            for time_b, task_b in placed[i + 1:]:
                if task_a.conflicts_with(task_b):
                    reports.append(ConflictReport(
                        task_a=task_a,
                        task_b=task_b,
                        time_a=time_a,
                        time_b=time_b,
                        same_pet=(task_a.pet_name == task_b.pet_name),
                    ))
        return reports

    def optimize_schedule(self, plan: DailyPlan) -> DailyPlan:
        """Re-generates the plan for the same date, applying all current tasks
        and availability.  Useful after adding/removing tasks or changing slots."""
        return self.generate_daily_plan(plan.date)

    @staticmethod
    def create_next_occurrence(task: CareTask) -> Optional[CareTask]:
        """Returns a fresh copy of a completed recurring task reset for its next occurrence.

        The copy has is_completed=False, scheduled_start_minute=None, and
        next_due_date=None so the scheduler treats it as a new pending task.
        Returns None if the task has no next_due_date (i.e. was never completed
        via mark_complete, or has a non-recurring frequency).
        """
        if task.next_due_date is None:
            return None
        return replace(task, is_completed=False, scheduled_start_minute=None, next_due_date=None)

    @staticmethod
    def sort_by_time(tasks: list[tuple[str, CareTask]]) -> list[tuple[str, CareTask]]:
        """Returns tasks sorted chronologically by scheduled_start_minute.
        Falls back to parsing the time string when scheduled_start_minute is not set.
        """
        def _key(item: tuple[str, CareTask]) -> int:
            time_str, task = item
            if task.scheduled_start_minute is not None:
                return task.scheduled_start_minute
            h, m = map(int, time_str.split(':'))
            return h * 60 + m

        return sorted(tasks, key=_key)


# ---------------------------------------------------------------------------
# Example usage (for testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pet = Pet(
        name="Buddy",
        species="dog",
        breed="Golden Retriever",
        age=3,
        weight=30.0,
        special_needs=["high energy"],
        medical_conditions=[]
    )

    morning_walk = CareTask(
        task_type="walk",
        name="Morning Walk",
        duration_minutes=30,
        priority=4,
        frequency="daily",
        preferred_time_windows=["07:00-09:00"]
    )

    feeding = CareTask(
        task_type="feed",
        name="Breakfast",
        duration_minutes=10,
        priority=5,
        frequency="daily",
        preferred_time_windows=["07:00-08:00"],
        is_time_flexible=False
    )

    pet.add_care_task(morning_walk)
    pet.add_care_task(feeding)

    owner = Owner(
        name="Alice",
        available_time_slots=["07:00-09:00", "12:00-13:00", "17:00-20:00"],
        preferences={"early_walks": True},
        total_available_minutes=300
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(date.today())

    print(f"Owner: {owner.name}")
    print(f"Pet: {pet.name} ({pet.breed})")
    print(f"Total tasks: {len(owner.get_all_care_tasks())}")
    print(f"\nPlan for {plan.date}:")
    print(f"  Scheduled:   {len(plan.scheduled_tasks)} tasks")
    print(f"  Unscheduled: {len(plan.unscheduled_tasks)} tasks")
    print(f"  Reasoning:   {plan.reasoning}")
    for time_str, task in plan.scheduled_tasks:
        print(f"  {time_str}  {task.name} ({task.duration_minutes}min)")
