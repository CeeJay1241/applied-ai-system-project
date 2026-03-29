"""
PawPal+ Care Knowledge Base
Source data for Retrieval-Augmented Generation (RAG) used by the AI advisor.
Each entry is tagged so it can be scored against a pet's profile at query time.
"""

from __future__ import annotations


CARE_KNOWLEDGE: list[dict] = [
    # ── Dogs ──────────────────────────────────────────────────────────────
    {
        "id": "dog_exercise_adult",
        "title": "Daily Exercise — Adult Dogs",
        "tags": {"species": ["dog"], "age_groups": ["adult"], "conditions": []},
        "content": (
            "Adult dogs need 30–60 minutes of moderate exercise daily. "
            "High-energy breeds (Husky, Border Collie, Vizsla, Jack Russell Terrier, Dalmatian) "
            "need 60–90+ minutes. Exercise prevents obesity, boredom-based destructive behaviour, "
            "and anxiety. Split into morning and evening walks for best results."
        ),
        "task_templates": [
            {"task_type": "walk", "name": "Morning Walk", "duration_minutes": 30,
             "priority": 4, "frequency": "daily", "preferred_time_windows": ["07:00-09:00"],
             "notes": "Keep consistent start time — dogs thrive on routine."},
            {"task_type": "walk", "name": "Evening Walk", "duration_minutes": 30,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["17:00-19:30"],
             "notes": "Good for mental stimulation after the owner's workday."},
        ],
    },
    {
        "id": "dog_exercise_puppy",
        "title": "Exercise — Puppies (under 2 years)",
        "tags": {"species": ["dog"], "age_groups": ["puppy"], "conditions": []},
        "content": (
            "Puppies should follow the '5-minute rule': 5 minutes of exercise per month of age, "
            "twice daily. Over-exercising puppies risks joint damage. Short, frequent play sessions "
            "are better than long walks. Training sessions double as mental exercise."
        ),
        "task_templates": [
            {"task_type": "walk", "name": "Puppy Walk", "duration_minutes": 15,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["08:00-09:00"],
             "notes": "Keep short — follow the 5-min per month of age rule."},
            {"task_type": "enrichment", "name": "Puppy Play Session", "duration_minutes": 15,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["16:00-18:00"],
             "notes": "Free play to burn energy without stressing developing joints."},
        ],
    },
    {
        "id": "dog_exercise_senior",
        "title": "Exercise — Senior Dogs (7+ years)",
        "tags": {"species": ["dog"], "age_groups": ["senior"], "conditions": []},
        "content": (
            "Senior dogs still need daily activity but should have shorter, gentler walks. "
            "20–30 minutes twice a day suits most seniors. Watch for signs of fatigue, stiffness, "
            "or limping. Swimming is excellent low-impact exercise for older dogs with joint issues."
        ),
        "task_templates": [
            {"task_type": "walk", "name": "Gentle Morning Walk", "duration_minutes": 20,
             "priority": 4, "frequency": "daily", "preferred_time_windows": ["08:00-10:00"],
             "notes": "Gentle pace — let the dog set the tempo. Watch for stiffness."},
        ],
    },
    {
        "id": "dog_feeding",
        "title": "Feeding Schedule — Adult/Senior Dogs",
        "tags": {"species": ["dog"], "age_groups": ["adult", "senior"], "conditions": []},
        "content": (
            "Adult dogs should be fed twice daily, 8–12 hours apart. "
            "Consistent mealtimes support digestion and prevent bloat. "
            "Do not exercise vigorously within 1 hour before or after meals (especially large breeds "
            "prone to GDV/bloat: Great Dane, Weimaraner, Saint Bernard, Standard Poodle)."
        ),
        "task_templates": [
            {"task_type": "feed", "name": "Breakfast", "duration_minutes": 10,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["07:00-08:00"],
             "is_time_flexible": False, "notes": "Consistent time each day."},
            {"task_type": "feed", "name": "Dinner", "duration_minutes": 10,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["17:00-18:00"],
             "is_time_flexible": False, "notes": "At least 1 hour after any vigorous exercise."},
        ],
    },
    {
        "id": "dog_feeding_puppy",
        "title": "Feeding Schedule — Puppies",
        "tags": {"species": ["dog"], "age_groups": ["puppy"], "conditions": []},
        "content": (
            "Puppies under 6 months need 3 meals a day. From 6 months, twice daily is appropriate. "
            "Consistent timing helps house-training — puppies typically need to eliminate "
            "15–30 minutes after eating."
        ),
        "task_templates": [
            {"task_type": "feed", "name": "Breakfast", "duration_minutes": 10,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["07:00-08:00"],
             "is_time_flexible": False},
            {"task_type": "feed", "name": "Lunch", "duration_minutes": 10,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["12:00-13:00"],
             "is_time_flexible": False, "notes": "Reduce to twice daily after 6 months."},
            {"task_type": "feed", "name": "Dinner", "duration_minutes": 10,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["17:00-18:00"],
             "is_time_flexible": False},
        ],
    },
    {
        "id": "dog_grooming",
        "title": "Grooming — Dogs",
        "tags": {"species": ["dog"], "age_groups": ["puppy", "adult", "senior"], "conditions": []},
        "content": (
            "Regular brushing reduces shedding and matting. Short-coated breeds (Beagle, Boxer) "
            "need weekly brushing; medium-coated (Labrador, Golden Retriever) 2–3x/week; "
            "long-coated (Shih Tzu, Afghan Hound, Collie) daily. "
            "Nails should be trimmed every 3–4 weeks."
        ),
        "task_templates": [
            {"task_type": "grooming", "name": "Coat Brushing", "duration_minutes": 15,
             "priority": 2, "frequency": "weekly", "preferred_time_windows": ["10:00-12:00"],
             "notes": "Adjust frequency to coat length. Check ears and nails too."},
        ],
    },
    # ── Cats ──────────────────────────────────────────────────────────────
    {
        "id": "cat_feeding",
        "title": "Feeding Schedule — Cats",
        "tags": {"species": ["cat"], "age_groups": ["kitten", "adult", "senior"], "conditions": []},
        "content": (
            "Adult cats do well on twice-daily measured meals. Free-feeding dry food contributes to "
            "obesity. Wet food once daily supports urinary health and hydration. "
            "Fresh water should always be available; many cats prefer a running-water fountain."
        ),
        "task_templates": [
            {"task_type": "feed", "name": "Breakfast", "duration_minutes": 5,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["07:00-08:00"],
             "is_time_flexible": False},
            {"task_type": "feed", "name": "Dinner", "duration_minutes": 5,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["17:00-18:00"],
             "is_time_flexible": False},
        ],
    },
    {
        "id": "cat_enrichment",
        "title": "Enrichment & Play — Cats",
        "tags": {"species": ["cat"], "age_groups": ["kitten", "adult"], "conditions": []},
        "content": (
            "Indoor cats need 15–30 minutes of interactive play daily to prevent boredom and obesity. "
            "Play mimics hunting behaviour (chase, pounce, catch). "
            "Feather wands, laser pointers, and puzzle feeders are highly effective. "
            "Two short sessions (morning and evening) are better than one long session."
        ),
        "task_templates": [
            {"task_type": "enrichment", "name": "Interactive Play", "duration_minutes": 15,
             "priority": 3, "frequency": "daily",
             "preferred_time_windows": ["07:30-09:00", "18:00-20:00"],
             "notes": "Feather toy or interactive puzzle feeder."},
        ],
    },
    {
        "id": "cat_grooming",
        "title": "Grooming — Cats",
        "tags": {"species": ["cat"], "age_groups": ["adult", "senior"], "conditions": []},
        "content": (
            "Short-haired cats are largely self-grooming; weekly brushing reduces hairballs. "
            "Long-haired breeds (Persian, Maine Coon, Ragdoll) need daily brushing to prevent mats. "
            "Senior cats may struggle to groom themselves — check for matting and skin conditions weekly."
        ),
        "task_templates": [
            {"task_type": "grooming", "name": "Coat Brushing", "duration_minutes": 10,
             "priority": 2, "frequency": "weekly", "preferred_time_windows": ["10:00-12:00"],
             "notes": "Check for mats, lumps, and skin issues during brushing."},
        ],
    },
    {
        "id": "cat_litter",
        "title": "Litter Box Maintenance",
        "tags": {"species": ["cat"], "age_groups": ["kitten", "adult", "senior"], "conditions": []},
        "content": (
            "Scoop litter at least once daily — cats avoid dirty boxes and may eliminate elsewhere. "
            "Full litter change and box wash every 1–2 weeks. "
            "Rule of thumb: one litter box per cat, plus one extra."
        ),
        "task_templates": [
            {"task_type": "enrichment", "name": "Litter Box Clean", "duration_minutes": 5,
             "priority": 4, "frequency": "daily", "preferred_time_windows": ["07:00-09:00"],
             "notes": "Scoop daily; full change weekly."},
        ],
    },
    # ── Medical conditions ─────────────────────────────────────────────────
    {
        "id": "condition_diabetes",
        "title": "Care for Diabetic Pets",
        "tags": {"species": ["dog", "cat"], "age_groups": [],
                 "conditions": ["diabetes", "diabetic"]},
        "content": (
            "Diabetic pets MUST be fed on a strict schedule tied to insulin injections. "
            "Meals should occur 30 minutes before insulin administration. "
            "Consistent carbohydrate intake per meal is critical for glucose control. "
            "Monitor for hypoglycaemia (weakness, trembling) between meals."
        ),
        "task_templates": [
            {"task_type": "medication", "name": "Insulin Injection", "duration_minutes": 10,
             "priority": 5, "frequency": "twice_daily",
             "preferred_time_windows": ["07:30-08:00", "19:30-20:00"],
             "is_time_flexible": False,
             "notes": "Administer after the pet has started eating. Consult vet for dose."},
        ],
    },
    {
        "id": "condition_joint",
        "title": "Joint & Arthritis Care",
        "tags": {"species": ["dog", "cat"], "age_groups": ["senior"],
                 "conditions": ["arthritis", "joint", "hip dysplasia", "mobility",
                                 "osteoarthritis", "senior joint"]},
        "content": (
            "Pets with joint issues benefit from low-impact exercise (short walks, hydrotherapy). "
            "Avoid high-impact activities like jumping or rough play. "
            "Joint supplements (glucosamine, omega-3s) should be given consistently with meals. "
            "Raised food and water bowls reduce neck/shoulder strain."
        ),
        "task_templates": [
            {"task_type": "medication", "name": "Joint Supplement", "duration_minutes": 5,
             "priority": 4, "frequency": "daily", "preferred_time_windows": ["07:00-08:30"],
             "is_time_flexible": False,
             "notes": "Give with food. Glucosamine/chondroitin or omega-3 fatty acids."},
        ],
    },
    {
        "id": "condition_dental",
        "title": "Dental Hygiene",
        "tags": {"species": ["dog", "cat"], "age_groups": ["adult", "senior"],
                 "conditions": ["dental disease", "gingivitis", "periodontal", "dental"]},
        "content": (
            "Dental disease is the most common health issue in pets. "
            "Daily tooth brushing reduces plaque by 70%. Use pet-safe toothpaste only — "
            "human toothpaste (xylitol) is toxic to pets. "
            "Dental chews and water additives provide secondary support."
        ),
        "task_templates": [
            {"task_type": "grooming", "name": "Tooth Brushing", "duration_minutes": 5,
             "priority": 4, "frequency": "daily", "preferred_time_windows": ["07:30-09:00"],
             "notes": "Use pet-specific toothpaste only (human toothpaste is toxic)."},
        ],
    },
    {
        "id": "condition_kidney",
        "title": "Kidney Disease Care",
        "tags": {"species": ["dog", "cat"], "age_groups": ["adult", "senior"],
                 "conditions": ["kidney disease", "renal failure", "CKD",
                                 "chronic kidney", "renal"]},
        "content": (
            "Pets with kidney disease need increased hydration — wet food or water fountains help. "
            "Low-phosphorus diet is essential; consult your vet for appropriate food. "
            "Small, frequent meals may be better tolerated. "
            "Monitor water intake and urination frequency daily."
        ),
        "task_templates": [
            {"task_type": "health_check", "name": "Water Intake Check", "duration_minutes": 5,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["19:00-21:00"],
             "notes": "Note if intake is significantly above or below normal — report to vet."},
        ],
    },
    {
        "id": "general_senior",
        "title": "Senior Pet Health Monitoring",
        "tags": {"species": ["dog", "cat"], "age_groups": ["senior"], "conditions": []},
        "content": (
            "Pets are considered senior at 7–10 years depending on species and size. "
            "Senior pets benefit from weekly weight checks (early warning for illness), "
            "monthly health assessments, and twice-yearly vet visits. "
            "Watch for changes in appetite, thirst, energy, and bathroom habits."
        ),
        "task_templates": [
            {"task_type": "health_check", "name": "Weekly Weight Check", "duration_minutes": 5,
             "priority": 3, "frequency": "weekly",
             "notes": "Record weight; flag >5% change in a week to your vet."},
        ],
    },
]


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def _age_group(species: str, age: int) -> str:
    """Map a pet's age to a life-stage label used for tag matching."""
    if species == "dog":
        return "puppy" if age < 2 else ("senior" if age >= 7 else "adult")
    if species == "cat":
        return "kitten" if age < 1 else ("senior" if age >= 10 else "adult")
    return "adult"


def retrieve_guidelines(pet) -> list[dict]:
    """Return the most relevant care guidelines for a given Pet.

    Scoring per entry:
      +3  species tag matches (or entry has no species restriction)
      +2  age_group tag matches (or entry has no age restriction)
      +4  any condition keyword found in pet.medical_conditions (substring, case-insensitive)
    Returns up to 8 entries with score > 0, sorted by score descending.
    """
    age_group = _age_group(pet.species, pet.age)
    conditions_lower = [c.lower() for c in getattr(pet, "medical_conditions", [])]

    scored: list[tuple[int, dict]] = []
    for entry in CARE_KNOWLEDGE:
        tags = entry["tags"]
        score = 0

        # Species match
        if not tags["species"] or pet.species in tags["species"]:
            score += 3

        # Age-group match
        if not tags["age_groups"] or age_group in tags["age_groups"]:
            score += 2

        # Medical condition match (substring both ways)
        for cond_tag in tags.get("conditions", []):
            for cond_pet in conditions_lower:
                if cond_tag.lower() in cond_pet or cond_pet in cond_tag.lower():
                    score += 4
                    break

        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:8]]
