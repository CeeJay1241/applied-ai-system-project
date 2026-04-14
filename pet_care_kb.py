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
# Second data source: Preventive & Behavioural Care
# ---------------------------------------------------------------------------

PREVENTIVE_CARE_KNOWLEDGE: list[dict] = [
    {
        "id": "prev_flea_tick",
        "title": "Flea & Tick Prevention",
        "tags": {"species": ["dog", "cat"], "age_groups": ["puppy", "adult", "senior"], "conditions": []},
        "content": (
            "Monthly flea and tick prevention is essential year-round, especially in warm climates. "
            "Untreated infestations lead to skin disease, anaemia, and tick-borne illness (Lyme disease, "
            "Rocky Mountain spotted fever). Use vet-approved topical treatments or oral tablets — "
            "never apply dog products to cats (permethrin is toxic to cats)."
        ),
        "task_templates": [
            {"task_type": "medication", "name": "Flea & Tick Treatment", "duration_minutes": 10,
             "priority": 4, "frequency": "weekly", "scheduled_weekday": 0,
             "notes": "Apply monthly. Use species-appropriate product only. Record date applied."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_heartworm",
        "title": "Heartworm Prevention — Dogs",
        "tags": {"species": ["dog"], "age_groups": ["puppy", "adult", "senior"], "conditions": []},
        "content": (
            "Heartworm disease is transmitted by mosquitoes and is potentially fatal if untreated. "
            "Monthly oral preventatives (e.g. ivermectin-based) are highly effective. "
            "Annual heartworm tests are recommended before restarting prevention after a lapse. "
            "Prevention is far cheaper than treatment."
        ),
        "task_templates": [
            {"task_type": "medication", "name": "Heartworm Prevention", "duration_minutes": 5,
             "priority": 4, "frequency": "weekly", "scheduled_weekday": 0,
             "notes": "Administer monthly. Never skip — even one missed dose can leave the dog vulnerable."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_anxiety_dog",
        "title": "Anxiety & Stress Management — Dogs",
        "tags": {"species": ["dog"], "age_groups": ["puppy", "adult", "senior"],
                 "conditions": ["anxiety", "stress", "separation anxiety", "nervous", "fearful",
                                 "reactive", "aggression"]},
        "content": (
            "Anxious dogs benefit from structured daily routines, adequate exercise, and mental enrichment. "
            "Decompression walks (letting the dog sniff freely) reduce cortisol levels significantly. "
            "Puzzle feeders and Kong toys extend engagement and reduce anxiety during alone time. "
            "Severe cases may need behaviour therapy or vet-prescribed anxiolytics — administer "
            "30–60 minutes before anticipated stressors (thunderstorms, visitors, car journeys)."
        ),
        "task_templates": [
            {"task_type": "enrichment", "name": "Decompression Sniff Walk", "duration_minutes": 20,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["07:00-09:00"],
             "notes": "Let the dog lead and sniff freely — no structured heel. Highly calming."},
            {"task_type": "enrichment", "name": "Puzzle Feeder Session", "duration_minutes": 15,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["12:00-14:00"],
             "notes": "Kong or snuffle mat with part of daily kibble. Reduces alone-time anxiety."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_weight_management",
        "title": "Weight Management & Obesity Prevention",
        "tags": {"species": ["dog", "cat"], "age_groups": ["adult", "senior"],
                 "conditions": ["obesity", "overweight", "weight", "diet"]},
        "content": (
            "Over 50% of pets in the US are overweight. Obesity shortens lifespan by up to 2 years "
            "and worsens joint disease, diabetes, and heart conditions. "
            "Measure meals precisely using a kitchen scale, not a cup. "
            "Treats should make up no more than 10% of daily caloric intake. "
            "Weekly weight checks allow early intervention before weight becomes hard to reverse."
        ),
        "task_templates": [
            {"task_type": "health_check", "name": "Weekly Weight Check", "duration_minutes": 5,
             "priority": 4, "frequency": "weekly",
             "notes": "Record weight on a chart. Target 0.5–1% body weight loss per week if on a diet."},
            {"task_type": "feed", "name": "Measured Meal — Morning", "duration_minutes": 10,
             "priority": 5, "frequency": "daily", "preferred_time_windows": ["07:00-08:00"],
             "is_time_flexible": False,
             "notes": "Use kitchen scale, not a cup. Consult vet for target calorie intake."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_vaccination",
        "title": "Vaccination & Vet Visit Reminders",
        "tags": {"species": ["dog", "cat"], "age_groups": ["puppy", "kitten", "adult", "senior"],
                 "conditions": []},
        "content": (
            "Core vaccines (rabies, distemper, parvovirus for dogs; FVRCP, rabies for cats) must be "
            "kept up to date. Puppies and kittens need boosters every 3–4 weeks until 16 weeks old. "
            "Adults need annual or triennial boosters depending on vaccine type. "
            "Senior pets benefit from twice-yearly vet check-ups to catch age-related issues early."
        ),
        "task_templates": [
            {"task_type": "health_check", "name": "Vet Check-up Reminder", "duration_minutes": 60,
             "priority": 3, "frequency": "weekly", "scheduled_weekday": 5,
             "notes": "Schedule biannual vet visits. Keep vaccination records updated."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_dental_prevention",
        "title": "Dental Disease Prevention",
        "tags": {"species": ["dog", "cat"], "age_groups": ["adult", "senior"], "conditions": []},
        "content": (
            "80% of dogs and 70% of cats show signs of dental disease by age 3. "
            "Daily brushing is the gold standard — even 3x/week makes a significant difference. "
            "Dental chews (VOHC-approved) provide secondary plaque control. "
            "Annual professional cleanings under anaesthesia are recommended for adult pets."
        ),
        "task_templates": [
            {"task_type": "grooming", "name": "Dental Chew", "duration_minutes": 10,
             "priority": 3, "frequency": "daily", "preferred_time_windows": ["18:00-20:00"],
             "notes": "VOHC-approved dental chew. Supplement to — not replacement for — brushing."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_socialisation",
        "title": "Socialisation & Mental Enrichment — Puppies",
        "tags": {"species": ["dog"], "age_groups": ["puppy"], "conditions": []},
        "content": (
            "The critical socialisation window closes at 12–14 weeks. Positive exposure to people, "
            "dogs, sounds, surfaces, and environments during this window prevents fear-based behaviour "
            "in adulthood. Training sessions also count as mental enrichment — 5–10 minutes twice daily "
            "is enough to build impulse control and a vocabulary of basic cues."
        ),
        "task_templates": [
            {"task_type": "training", "name": "Training & Socialisation", "duration_minutes": 10,
             "priority": 4, "frequency": "daily", "preferred_time_windows": ["09:00-10:00"],
             "notes": "Keep sessions short and positive. Focus on sit, stay, come, leave it."},
        ],
        "source": "preventive_care",
    },
    {
        "id": "prev_hyperthyroid_cat",
        "title": "Hyperthyroidism Management — Cats",
        "tags": {"species": ["cat"], "age_groups": ["senior"],
                 "conditions": ["hyperthyroidism", "thyroid", "hyperthyroid"]},
        "content": (
            "Feline hyperthyroidism is one of the most common senior cat conditions. "
            "Methimazole is typically given twice daily at 12-hour intervals. "
            "Monitor for side effects: vomiting, lethargy, facial scratching. "
            "Regular thyroid level checks (every 3–6 months once stabilised) are required. "
            "An iodine-restricted prescription diet is an alternative to daily medication."
        ),
        "task_templates": [
            {"task_type": "medication", "name": "Thyroid Medication", "duration_minutes": 5,
             "priority": 5, "frequency": "twice_daily",
             "preferred_time_windows": ["07:30-08:00", "19:30-20:00"],
             "is_time_flexible": False,
             "notes": "Give methimazole with a small amount of food to reduce nausea. 12-hour spacing."},
        ],
        "source": "preventive_care",
    },
]


# ---------------------------------------------------------------------------
# Body Condition Classifier
# ---------------------------------------------------------------------------

# Breed → size category mapping (keyword-based, case-insensitive)
_BREED_SIZE_MAP: list[tuple[list[str], str]] = [
    (["chihuahua", "pomeranian", "maltese", "yorkie", "yorkshire", "shih tzu", "papillon",
      "miniature pinscher", "min pin", "toy poodle", "miniature dachshund", "miniature schnauzer",
      "italian greyhound", "pekingese", "japanese chin"], "small"),
    (["beagle", "cocker spaniel", "border collie", "australian shepherd", "aussie", "whippet",
      "english springer", "brittany", "basenji", "bulldog", "french bulldog", "frenchie",
      "shar pei", "standard schnauzer", "staffordshire", "staffy", "pit bull", "pitbull",
      "american pit", "siberian husky", "husky", "shiba inu"], "medium"),
    (["labrador", "golden retriever", "german shepherd", "alsatian", "rottweiler", "boxer",
      "weimaraner", "doberman", "dobermann", "standard poodle", "dalmatian", "vizsla",
      "belgian malinois", "malinois", "flat coated retriever", "irish setter", "pointer"], "large"),
    (["great dane", "saint bernard", "mastiff", "newfoundland", "bernese mountain",
      "irish wolfhound", "leonberger", "great pyrenees", "anatolian", "kangal"], "giant"),
]

# Ideal weight ranges: (min_kg, max_kg) keyed by (species, life_stage, size)
_IDEAL_WEIGHT: dict[tuple, tuple[float, float]] = {
    # Dogs — puppies
    ("dog", "puppy", "small"):  (0.5, 4.0),
    ("dog", "puppy", "medium"): (5.0, 15.0),
    ("dog", "puppy", "large"):  (10.0, 25.0),
    ("dog", "puppy", "giant"):  (15.0, 40.0),
    # Dogs — adults
    ("dog", "adult", "small"):  (2.0, 6.0),
    ("dog", "adult", "medium"): (10.0, 25.0),
    ("dog", "adult", "large"):  (25.0, 40.0),
    ("dog", "adult", "giant"):  (45.0, 90.0),
    # Dogs — seniors (slightly lower ceiling — muscle loss expected)
    ("dog", "senior", "small"):  (2.0, 5.5),
    ("dog", "senior", "medium"): (9.0, 23.0),
    ("dog", "senior", "large"):  (23.0, 38.0),
    ("dog", "senior", "giant"):  (40.0, 80.0),
    # Cats
    ("cat", "kitten", "standard"): (0.5, 3.5),
    ("cat", "adult",  "standard"): (3.5, 5.5),
    ("cat", "senior", "standard"): (3.0, 5.0),  # floor drops — weight loss common in seniors
}


def _get_breed_size(breed: str) -> str:
    """Map a breed string to a size category. Defaults to 'medium' if unrecognised."""
    breed_lower = breed.lower()
    for keywords, size in _BREED_SIZE_MAP:
        if any(kw in breed_lower for kw in keywords):
            return size
    return "medium"


def assess_body_condition(species: str, breed: str, age: float, weight_kg: float) -> dict:
    """Assess a pet's body condition based on species, breed, age, and weight.

    Returns a dict with:
        status      — "healthy", "overweight", "obese", "underweight", or "unknown"
        label       — short human-readable label
        detail      — explanation string shown in the UI
        conditions  — list of condition strings to auto-inject into RAG (may be empty)
    """
    life_stage = _age_group(species, int(age))

    if species == "dog":
        size = _get_breed_size(breed)
        key = ("dog", life_stage, size)
    elif species == "cat":
        key = ("cat", life_stage, "standard")
    else:
        return {"status": "unknown", "label": "Not assessed",
                "detail": "Weight assessment is not available for this species.",
                "conditions": []}

    if key not in _IDEAL_WEIGHT:
        return {"status": "unknown", "label": "Not assessed",
                "detail": "Could not determine ideal weight range for this profile.",
                "conditions": []}

    ideal_min, ideal_max = _IDEAL_WEIGHT[key]

    if weight_kg > ideal_max * 1.20:
        return {
            "status": "obese",
            "label": "Obese",
            "detail": (
                f"At {weight_kg:.1f} kg, {breed or species} is significantly above the healthy range "
                f"of {ideal_min}–{ideal_max} kg for a {life_stage} of this size. "
                "Obesity increases risk of diabetes, joint disease, and heart conditions."
            ),
            "conditions": ["obesity", "overweight"],
        }
    if weight_kg > ideal_max * 1.10:
        return {
            "status": "overweight",
            "label": "Overweight",
            "detail": (
                f"At {weight_kg:.1f} kg, {breed or species} is above the healthy range "
                f"of {ideal_min}–{ideal_max} kg for a {life_stage} of this size. "
                "Weight management is recommended."
            ),
            "conditions": ["overweight"],
        }
    if weight_kg < ideal_min * 0.85:
        return {
            "status": "underweight",
            "label": "Underweight",
            "detail": (
                f"At {weight_kg:.1f} kg, {breed or species} is below the healthy range "
                f"of {ideal_min}–{ideal_max} kg for a {life_stage} of this size. "
                "Consider a vet visit to rule out underlying illness."
            ),
            "conditions": ["underweight"],
        }
    return {
        "status": "healthy",
        "label": "Healthy weight",
        "detail": (
            f"At {weight_kg:.1f} kg, {breed or species} is within the healthy range "
            f"of {ideal_min}–{ideal_max} kg for a {life_stage} of this size."
        ),
        "conditions": [],
    }


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


def _score_entry(entry: dict, species: str, age_group: str, conditions_lower: list[str]) -> int:
    """Score a single knowledge base entry against a pet's profile.

    +3  species tag matches (or entry has no species restriction)
    +2  age_group tag matches (or entry has no age restriction)
    +4  any condition keyword found in pet.medical_conditions (substring, case-insensitive)
    """
    tags = entry["tags"]
    score = 0

    if not tags["species"] or species in tags["species"]:
        score += 3

    if not tags["age_groups"] or age_group in tags["age_groups"]:
        score += 2

    for cond_tag in tags.get("conditions", []):
        for cond_pet in conditions_lower:
            if cond_tag.lower() in cond_pet or cond_pet in cond_tag.lower():
                score += 4
                break

    return score


def retrieve_guidelines(pet) -> list[dict]:
    """Return the most relevant care guidelines for a given Pet.

    Retrieves from two knowledge sources:
      - CARE_KNOWLEDGE        — core care guidelines (exercise, feeding, grooming, medical)
      - PREVENTIVE_CARE_KNOWLEDGE — preventive & behavioural guidelines (parasites, anxiety,
                                    weight, dental prevention, socialisation, vaccines)

    Before scoring, body condition assessment runs automatically on the pet's species,
    breed, age, and weight. If the pet is overweight, obese, or underweight, the relevant
    condition labels are injected into the scoring so appropriate guidelines surface without
    the owner having to self-diagnose.

    Scoring per entry:
      +3  species tag matches (or entry has no species restriction)
      +2  age_group tag matches (or entry has no age restriction)
      +4  any condition keyword found in pet.medical_conditions or BCS result (substring, case-insensitive)
    Returns up to 8 entries with score > 0, sorted by score descending.
    """
    age_group = _age_group(pet.species, pet.age)

    # Start with owner-declared conditions
    conditions_lower = [c.lower() for c in getattr(pet, "medical_conditions", [])]

    # Auto-inject BCS conditions based on species + breed + age + weight
    weight = getattr(pet, "weight", None) or getattr(pet, "weight_kg", None)
    breed = getattr(pet, "breed", "") or ""
    if weight:
        bcs = assess_body_condition(pet.species, breed, pet.age, weight)
        for auto_cond in bcs["conditions"]:
            if auto_cond not in conditions_lower:
                conditions_lower.append(auto_cond)

    all_entries = CARE_KNOWLEDGE + PREVENTIVE_CARE_KNOWLEDGE

    scored: list[tuple[int, dict]] = []
    for entry in all_entries:
        score = _score_entry(entry, pet.species, age_group, conditions_lower)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:8]]
