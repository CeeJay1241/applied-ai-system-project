"""
PawPal+ Evaluation Harness
==========================
Runs the core system components against predefined pet profiles and prints
a pass/fail summary. Zero API calls — all evaluation is deterministic.

Components tested:
  1. RAG Retrieval   — correct guidelines surface for each profile
  2. BCS Classifier  — correct body condition assessment (species + breed + age + weight)
  3. Scheduler       — correct task placement, priority ordering, recurrence
  4. Conflict Det.   — overlapping tasks correctly flagged / adjacent tasks not flagged

Run with:
    python eval.py
    python eval.py --verbose    # show detail on each check
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pawpal_system import CareTask, Owner, Pet, Scheduler
from pet_care_kb import assess_body_condition, retrieve_guidelines

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"
_results: list[tuple[str, str, str, str]] = []  # (section, label, status, detail)


def check(section: str, label: str, condition: bool, detail: str = "") -> None:
    status = PASS if condition else FAIL
    _results.append((section, label, status, detail))


# ---------------------------------------------------------------------------
# Section 1 — RAG Retrieval
# ---------------------------------------------------------------------------

def eval_rag() -> None:
    section = "RAG Retrieval"

    # Profile 1: diabetic senior dog — insulin guideline must surface
    dog = Pet(name="Rex", species="dog", breed="Labrador", age=9, weight=32.0,
              medical_conditions=["diabetes"])
    guidelines = retrieve_guidelines(dog)
    titles = [g["title"] for g in guidelines]
    check(section, "Diabetic dog: insulin guideline retrieved",
          any("Diabetic" in t or "diabet" in t.lower() for t in titles),
          f"Got: {titles[:3]}")

    # Profile 2: senior cat — senior-specific guideline must surface
    cat = Pet(name="Luna", species="cat", breed="Persian", age=12, weight=4.2)
    guidelines = retrieve_guidelines(cat)
    titles = [g["title"] for g in guidelines]
    check(section, "Senior cat: senior guideline retrieved",
          any("Senior" in t or "senior" in t.lower() for t in titles),
          f"Got: {titles[:3]}")

    # Profile 3: anxious dog — anxiety guideline must surface
    anxious = Pet(name="Pip", species="dog", breed="Beagle", age=3, weight=12.0,
                  medical_conditions=["anxiety"])
    guidelines = retrieve_guidelines(anxious)
    titles = [g["title"] for g in guidelines]
    check(section, "Anxious dog: anxiety guideline retrieved",
          any("Anxiety" in t or "anxiety" in t.lower() for t in titles),
          f"Got: {titles[:3]}")

    # Profile 4: hyperthyroid senior cat — thyroid guideline must surface
    hyper = Pet(name="Mochi", species="cat", breed="DSH", age=13, weight=3.8,
                medical_conditions=["hyperthyroidism"])
    guidelines = retrieve_guidelines(hyper)
    titles = [g["title"] for g in guidelines]
    check(section, "Hyperthyroid cat: thyroid guideline retrieved",
          any("Hyperthyroid" in t or "thyroid" in t.lower() for t in titles),
          f"Got: {titles[:3]}")

    # Profile 5: obese adult dog — weight management must surface automatically (no condition entered)
    # Chihuahua small range is 2-6kg, so 10kg is clearly obese → auto-injection should trigger
    fat_dog = Pet(name="Biscuit", species="dog", breed="Chihuahua", age=4, weight=10.0)
    guidelines = retrieve_guidelines(fat_dog)
    titles = [g["title"] for g in guidelines]
    check(section, "Obese dog (no explicit condition): weight guideline auto-injected",
          any("Weight" in t or "Obes" in t for t in titles),
          f"Got: {titles[:3]}")

    # Profile 6: puppy — puppy-specific guidelines must surface
    puppy = Pet(name="Max", species="dog", breed="Golden Retriever", age=1, weight=15.0)
    guidelines = retrieve_guidelines(puppy)
    titles = [g["title"] for g in guidelines]
    check(section, "Puppy: puppy-specific guideline retrieved",
          any("Pupp" in t or "puppy" in t.lower() for t in titles),
          f"Got: {titles[:3]}")

    # Profile 7: top result must be condition-specific when condition is present
    diabetic_cat = Pet(name="Cleo", species="cat", breed="Siamese", age=8, weight=4.5,
                       medical_conditions=["diabetes"])
    guidelines = retrieve_guidelines(diabetic_cat)
    top_title = guidelines[0]["title"] if guidelines else ""
    check(section, "Diabetic cat: top result is condition-specific",
          "diabet" in top_title.lower() or "Diabetic" in top_title,
          f"Top result: '{top_title}'")


# ---------------------------------------------------------------------------
# Section 2 — BCS Classifier
# ---------------------------------------------------------------------------

def eval_bcs() -> None:
    section = "BCS Classifier"

    cases = [
        # (species, breed, age, weight, expected_status, label)
        ("dog", "Labrador", 1,  30.0, "overweight",   "Labrador puppy 30kg → overweight"),
        ("dog", "Labrador", 4,  30.0, "healthy",       "Labrador adult 30kg → healthy"),
        ("dog", "Labrador", 9,  20.0, "healthy",       "Labrador senior 20kg → healthy"),
        ("dog", "Labrador", 9,  15.0, "underweight",   "Labrador senior 15kg → underweight"),
        ("dog", "Chihuahua", 3, 8.0,  "obese",         "Chihuahua adult 8kg → obese"),
        ("cat", "DSH",       0.5, 1.0, "healthy",      "Cat kitten 1kg → healthy"),
        ("cat", "DSH",       5,   1.0, "underweight",  "Cat adult 1kg → underweight"),
        ("cat", "DSH",       12,  6.5, "obese",        "Cat senior 6.5kg → obese"),
        ("cat", "Persian",   7,   5.0, "healthy",      "Cat adult 5kg → healthy"),
        ("other", "Rabbit",  2,   2.0, "unknown",      "Other species → unknown (not assessed)"),
    ]

    for species, breed, age, weight, expected, label in cases:
        result = assess_body_condition(species, breed, age, weight)
        check(section, label, result["status"] == expected,
              f"Expected '{expected}', got '{result['status']}'")


# ---------------------------------------------------------------------------
# Section 3 — Scheduler
# ---------------------------------------------------------------------------

def _make_owner(slots: list[str]) -> Owner:
    return Owner(name="Eval Owner", available_time_slots=slots)


def eval_scheduler() -> None:
    section = "Scheduler"

    # 3a: High-priority task scheduled before low-priority
    owner = _make_owner(["07:00-09:00"])
    pet = Pet(name="A", species="dog", breed="Lab", age=3, weight=30.0)
    high = CareTask(task_type="medication", name="Meds", duration_minutes=10,
                    priority=5, frequency="daily")
    low = CareTask(task_type="walk", name="Walk", duration_minutes=10,
                   priority=1, frequency="daily")
    pet.add_care_task(low)
    pet.add_care_task(high)
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_daily_plan(date.today())
    scheduled_names = [t.name for _, t in plan.scheduled_tasks]
    check(section, "High-priority task scheduled before low-priority",
          scheduled_names.index("Meds") < scheduled_names.index("Walk"),
          f"Order: {scheduled_names}")

    # 3b: Task that fits preferred window is placed there
    owner2 = _make_owner(["07:00-09:00", "17:00-20:00"])
    pet2 = Pet(name="B", species="dog", breed="Lab", age=3, weight=30.0)
    windowed = CareTask(task_type="walk", name="Morning Walk", duration_minutes=30,
                        priority=3, frequency="daily",
                        preferred_time_windows=["07:00-08:00"])
    pet2.add_care_task(windowed)
    owner2.add_pet(pet2)
    plan2 = Scheduler(owner2).generate_daily_plan(date.today())
    placed = next((t for _, t in plan2.scheduled_tasks if t.name == "Morning Walk"), None)
    check(section, "Task placed in preferred time window",
          placed is not None and placed.scheduled_start_minute == 420,
          f"start_minute={placed.scheduled_start_minute if placed else 'not scheduled'}")

    # 3c: Task that doesn't fit is unscheduled
    owner3 = _make_owner(["07:00-07:30"])
    pet3 = Pet(name="C", species="dog", breed="Lab", age=3, weight=30.0)
    big = CareTask(task_type="walk", name="Long Walk", duration_minutes=60,
                   priority=3, frequency="daily")
    pet3.add_care_task(big)
    owner3.add_pet(pet3)
    plan3 = Scheduler(owner3).generate_daily_plan(date.today())
    check(section, "Task exceeding slot capacity goes to unscheduled",
          len(plan3.unscheduled_tasks) == 1 and len(plan3.scheduled_tasks) == 0,
          f"scheduled={len(plan3.scheduled_tasks)}, unscheduled={len(plan3.unscheduled_tasks)}")

    # 3d: Weekly task skipped on wrong weekday
    owner4 = _make_owner(["07:00-09:00"])
    pet4 = Pet(name="D", species="dog", breed="Lab", age=3, weight=30.0)
    tuesday = date(2026, 4, 14)  # Tuesday
    weekly = CareTask(task_type="grooming", name="Grooming", duration_minutes=20,
                      priority=3, frequency="weekly", scheduled_weekday=0)  # Monday
    pet4.add_care_task(weekly)
    owner4.add_pet(pet4)
    plan4 = Scheduler(owner4).generate_daily_plan(tuesday)
    all_names4 = [t.name for _, t in plan4.scheduled_tasks] + [t.name for t in plan4.unscheduled_tasks]
    check(section, "Weekly task skipped on wrong weekday",
          "Grooming" not in all_names4,
          f"Found in plan: {'Grooming' in all_names4}")

    # 3e: Weekly task included on correct weekday
    monday = date(2026, 4, 13)
    plan5 = Scheduler(owner4).generate_daily_plan(monday)
    check(section, "Weekly task included on correct weekday",
          any(t.name == "Grooming" for _, t in plan5.scheduled_tasks),
          f"scheduled={[t.name for _, t in plan5.scheduled_tasks]}")

    # 3f: Completed task skipped when next_due_date is in the future
    owner5 = _make_owner(["07:00-09:00"])
    pet5 = Pet(name="E", species="dog", breed="Lab", age=3, weight=30.0)
    done_task = CareTask(task_type="feed", name="Breakfast", duration_minutes=10,
                         priority=5, frequency="daily")
    today = date.today()
    done_task.mark_complete(on_date=today)  # next_due_date = tomorrow
    pet5.add_care_task(done_task)
    owner5.add_pet(pet5)
    plan6 = Scheduler(owner5).generate_daily_plan(today)
    all_names6 = [t.name for _, t in plan6.scheduled_tasks] + [t.name for t in plan6.unscheduled_tasks]
    check(section, "Completed task excluded when next_due_date is future",
          "Breakfast" not in all_names6,
          f"Found in plan: {'Breakfast' in all_names6}")

    # 3g: Auto-generated puppy training task appears
    owner6 = _make_owner(["09:00-11:00"])
    pet6 = Pet(name="Pup", species="dog", breed="Lab", age=1, weight=10.0)
    owner6.add_pet(pet6)
    plan7 = Scheduler(owner6).generate_daily_plan(date.today())
    check(section, "Auto-generated puppy training task scheduled",
          any("Training" in t.name for _, t in plan7.scheduled_tasks),
          f"scheduled={[t.name for _, t in plan7.scheduled_tasks]}")

    # 3h: Twice-daily task expands to two instances
    owner7 = _make_owner(["07:00-09:00", "17:00-20:00"])
    pet7 = Pet(name="F", species="cat", breed="DSH", age=4, weight=4.5)
    twice = CareTask(task_type="feed", name="Meals", duration_minutes=10,
                     priority=5, frequency="twice_daily",
                     preferred_time_windows=["07:00-09:00", "17:00-20:00"])
    pet7.add_care_task(twice)
    owner7.add_pet(pet7)
    plan8 = Scheduler(owner7).generate_daily_plan(date.today())
    check(section, "Twice-daily task expands to two scheduled instances",
          len(plan8.scheduled_tasks) == 2,
          f"scheduled count={len(plan8.scheduled_tasks)}")


# ---------------------------------------------------------------------------
# Section 4 — Conflict Detection
# ---------------------------------------------------------------------------

def eval_conflicts() -> None:
    from pawpal_system import DailyPlan
    section = "Conflict Detection"

    # 4a: Overlapping tasks flagged
    task_a = CareTask(task_type="walk", name="Walk", duration_minutes=30,
                      priority=4, frequency="daily",
                      pet_name="Buddy", scheduled_start_minute=420)  # 07:00-07:30
    task_b = CareTask(task_type="feed", name="Feed", duration_minutes=20,
                      priority=5, frequency="daily",
                      pet_name="Buddy", scheduled_start_minute=430)  # 07:10-07:30
    plan = DailyPlan(date=date.today())
    plan.scheduled_tasks = [("07:00", task_a), ("07:10", task_b)]
    reports = Scheduler(Owner(name="Eval")).detect_conflicts(plan)
    check(section, "Overlapping tasks flagged as conflict",
          len(reports) == 1,
          f"conflicts found: {len(reports)}")

    # 4b: Adjacent tasks not flagged
    task_c = CareTask(task_type="feed", name="Breakfast", duration_minutes=10,
                      priority=5, frequency="daily",
                      pet_name="Buddy", scheduled_start_minute=450)  # 07:30-07:40
    plan2 = DailyPlan(date=date.today())
    plan2.scheduled_tasks = [("07:00", task_a), ("07:30", task_c)]
    reports2 = Scheduler(Owner(name="Eval")).detect_conflicts(plan2)
    check(section, "Adjacent tasks not flagged as conflict",
          len(reports2) == 0,
          f"conflicts found: {len(reports2)}")

    # 4c: Same-pet conflict classified correctly
    check(section, "Same-pet overlap classified as same_pet=True",
          len(reports) == 1 and reports[0].same_pet is True,
          f"same_pet={reports[0].same_pet if reports else 'N/A'}")

    # 4d: Cross-pet conflict classified correctly
    task_d = CareTask(task_type="walk", name="Walk Mittens", duration_minutes=30,
                      priority=3, frequency="daily",
                      pet_name="Mittens", scheduled_start_minute=430)  # overlaps with task_a
    plan3 = DailyPlan(date=date.today())
    plan3.scheduled_tasks = [("07:00", task_a), ("07:10", task_d)]
    reports3 = Scheduler(Owner(name="Eval")).detect_conflicts(plan3)
    check(section, "Cross-pet overlap classified as same_pet=False",
          len(reports3) == 1 and reports3[0].same_pet is False,
          f"same_pet={reports3[0].same_pet if reports3 else 'N/A'}")

    # 4e: Empty plan returns no reports
    empty_plan = DailyPlan(date=date.today())
    reports4 = Scheduler(Owner(name="Eval")).detect_conflicts(empty_plan)
    check(section, "Empty plan returns no conflict reports",
          reports4 == [],
          f"reports: {reports4}")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(verbose: bool) -> int:
    sections: dict[str, list] = {}
    for section, label, status, detail in _results:
        sections.setdefault(section, []).append((label, status, detail))

    total = len(_results)
    passed = sum(1 for *_, s, _ in _results if s == PASS)
    failed = total - passed

    print()
    print("=" * 62)
    print("  PawPal+ Evaluation Harness")
    print("=" * 62)

    for section, items in sections.items():
        sec_pass = sum(1 for _, s, _ in items if s == PASS)
        sec_total = len(items)
        print(f"\n  {section} ({sec_pass}/{sec_total})")
        print("  " + "-" * 50)
        for label, status, detail in items:
            icon = "✓" if status == PASS else "✗"
            print(f"  [{icon}] {label}")
            if verbose and detail:
                print(f"       {detail}")

    print()
    print("=" * 62)
    print(f"  Results: {passed}/{total} passed", end="")
    if failed:
        print(f"  ({failed} FAILED)")
    else:
        print("  — all checks passed")
    print("=" * 62)
    print()

    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PawPal+ evaluation harness")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detail on each check")
    args = parser.parse_args()

    eval_rag()
    eval_bcs()
    eval_scheduler()
    eval_conflicts()

    sys.exit(print_report(args.verbose))
