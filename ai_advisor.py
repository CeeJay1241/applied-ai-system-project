"""
PawPal+ AI Care Advisor
Agentic workflow powered by Gemini with function calling.

How it works
------------
1. RAG  — retrieve_guidelines() scores the knowledge base against the pet's
   profile (species, age, medical conditions) and injects the top matches
   into the system prompt so the model has grounded, specific context.

2. Agentic loop — the agent is given three tools:
     • get_existing_tasks   — inspect what's already on the pet's schedule
     • suggest_task         — add a task to the emerging care plan
     • finalize_plan        — end the loop with a natural-language summary

   The loop runs until the agent calls finalize_plan or hits the turn cap.
   Function responses are fed back so the model can observe each outcome
   and adjust (standard agentic pattern).
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
import time

from google import genai
from google.genai import types, errors as genai_errors
from dotenv import load_dotenv

load_dotenv()  # load GOOGLE_API_KEY from .env if present

from pawpal_system import CareTask, Pet
from pet_care_kb import retrieve_guidelines

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("pawpal.ai_advisor")

_TIME_OF_DAY_ALIASES = {
    "morning": "morning",
    "am": "morning",
    "breakfast": "morning",
    "afternoon": "afternoon",
    "lunch": "afternoon",
    "evening": "evening",
    "pm": "evening",
    "night": "night",
    "dinner": "night",
}


def _send_message_with_retry(chat, message, *, max_retries: int = 3):
    """Send a chat message with bounded retry on transient API throttling/errors."""
    for attempt in range(max_retries + 1):
        try:
            return chat.send_message(message)
        except genai_errors.ClientError as exc:
            error_text = str(exc).lower()
            # Hard quota exhaustion will not succeed with retries.
            if "exceeded your current quota" in error_text or "check your plan and billing" in error_text:
                raise
            if exc.code != 429 or attempt >= max_retries:
                raise
            # Exponential backoff with jitter to reduce retry collisions.
            delay = (2 ** attempt) + random.uniform(0.1, 0.5)
            log.warning(
                "Gemini rate-limited (429). Retrying in %.2fs (%d/%d)",
                delay,
                attempt + 1,
                max_retries,
            )
            time.sleep(delay)
        except genai_errors.ServerError:
            if attempt >= max_retries:
                raise
            delay = (2 ** attempt) + random.uniform(0.1, 0.5)
            log.warning(
                "Gemini server error. Retrying in %.2fs (%d/%d)",
                delay,
                attempt + 1,
                max_retries,
            )
            time.sleep(delay)


def _normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _extract_time_of_day(name: str) -> str | None:
    normalized = _normalize_name(name)
    for token, canonical in _TIME_OF_DAY_ALIASES.items():
        if re.search(rf"\b{re.escape(token)}\b", normalized):
            return canonical
    return None


def _canonical_task_key(task_type: str, name: str) -> str:
    time_of_day = _extract_time_of_day(name)
    if time_of_day:
        return f"{task_type}:{time_of_day}"
    return f"{task_type}:{_normalize_name(name)}"


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _build_system_prompt(pet: Pet, guidelines: list[dict]) -> str:
    """Build the system prompt, embedding the retrieved care knowledge."""
    kb_text = "\n\n".join(
        f"### {g['title']}\n{g['content']}"
        for g in guidelines
    )
    conditions_str = ", ".join(pet.medical_conditions) if pet.medical_conditions else "None"
    needs_str = ", ".join(pet.special_needs) if pet.special_needs else "None"

    return f"""\
You are PawPal+'s AI Care Advisor. Your job is to create a personalised, \
practical daily care plan for a specific pet, grounded in veterinary best practices.

## Pet Profile
- Name: {pet.name}
- Species: {pet.species}
- Breed: {pet.breed}
- Age: {pet.age} year(s)
- Weight: {pet.weight} kg
- Special needs: {needs_str}
- Medical conditions: {conditions_str}

## Relevant Care Guidelines (retrieved from knowledge base)
{kb_text}

## Your Task
Using the pet profile and the care guidelines above, build an appropriate set \
of daily care tasks.

Workflow:
1. Call get_existing_tasks first to see what tasks are already scheduled.
2. Call suggest_task for each new task that is genuinely relevant and not \
   already covered.
3. Call finalize_plan once with a concise explanation of your recommendations \
   and the reasoning behind each one.

Rules:
- Only suggest tasks relevant to this specific pet's profile and conditions.
- Do NOT suggest tasks whose names are already in the existing task list.
- If a task name is time-of-day specific (e.g., morning/evening), set frequency
    to daily (single session), not twice_daily.
- Prioritise medical/medication tasks (priority 4-5) and time-critical tasks.
- Be specific: use durations and time windows consistent with the guidelines.
- Suggest no more than 7 tasks total.
- If the existing tasks already cover the pet's needs well, suggest nothing \
  new and explain that in finalize_plan.
"""


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="get_existing_tasks",
            description="Returns the names of care tasks already added for this pet.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            ),
        ),
        types.FunctionDeclaration(
            name="suggest_task",
            description="Suggests a new care task to add to the pet's schedule.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "task_type": types.Schema(
                        type="STRING",
                        enum=["walk", "feed", "medication", "grooming",
                              "enrichment", "training", "health_check"],
                        description="Category of care task.",
                    ),
                    "name": types.Schema(
                        type="STRING",
                        description="Short descriptive task name.",
                    ),
                    "duration_minutes": types.Schema(
                        type="INTEGER",
                        description="How long the task takes in minutes.",
                    ),
                    "priority": types.Schema(
                        type="INTEGER",
                        description="1=low importance, 5=critical.",
                    ),
                    "frequency": types.Schema(
                        type="STRING",
                        enum=["daily", "twice_daily", "weekly"],
                        description="How often the task recurs.",
                    ),
                    "preferred_time_windows": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description=(
                            "Optional HH:MM-HH:MM windows. Provide 2 for "
                            "twice_daily tasks (AM first, then PM)."
                        ),
                    ),
                    "is_time_flexible": types.Schema(
                        type="BOOLEAN",
                        description=(
                            "Set False for tasks that must happen at the "
                            "specified time (e.g. medication). Defaults to True."
                        ),
                    ),
                    "notes": types.Schema(
                        type="STRING",
                        description="Optional care instruction or context for the owner.",
                    ),
                },
                required=["task_type", "name", "duration_minutes", "priority", "frequency"],
            ),
        ),
        types.FunctionDeclaration(
            name="finalize_plan",
            description=(
                "Call this when you have finished suggesting tasks. "
                "Provide a summary of what was recommended and why."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "explanation": types.Schema(
                        type="STRING",
                        description=(
                            "Natural language explanation of the suggested tasks "
                            "and the reasoning behind each recommendation."
                        ),
                    ),
                },
                required=["explanation"],
            ),
        ),
    ])
]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_ai_advisor(
    pet: Pet,
    existing_tasks: list[CareTask],
) -> dict:
    """Run the agentic care advisor for *pet*.

    Parameters
    ----------
    pet:
        The Pet object whose profile drives retrieval and suggestions.
    existing_tasks:
        CareTask objects already on the pet's schedule (used to avoid duplicates
        and shape smarter suggestions).

    Returns
    -------
    dict with keys:
        tasks       – list[CareTask] suggested by the agent
        explanation – agent's natural-language reasoning string
        error       – str if something went wrong, else None
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        log.error("GOOGLE_API_KEY is not set")
        return {
            "tasks": [],
            "explanation": "",
            "error": (
                "GOOGLE_API_KEY environment variable is not set. "
                "Add it to a .env file (see .env.example) or export it in your shell."
            ),
        }

    client = genai.Client(api_key=api_key)

    # RAG: score and retrieve relevant guidelines
    guidelines = retrieve_guidelines(pet)
    log.info(
        "RAG: retrieved %d guidelines for %s (%s, age %d, conditions: %s)",
        len(guidelines),
        pet.name,
        pet.species,
        pet.age,
        pet.medical_conditions or "none",
    )

    system_prompt = _build_system_prompt(pet, guidelines)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    existing_task_names = [t.name for t in existing_tasks]
    existing_name_keys = {_normalize_name(t.name) for t in existing_tasks}
    existing_canonical_keys = {
        _canonical_task_key(t.task_type, t.name) for t in existing_tasks
    }

    chat = client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=TOOLS,
        ),
    )
    log.info("Using Gemini model: %s", model_name)

    suggested_tasks: list[CareTask] = []
    explanation = ""
    done = False
    max_turns = 10  # safety cap on agentic loop iterations

    try:
        response = _send_message_with_retry(
            chat,
            f"Please suggest a personalised care plan for {pet.name}. "
            "Start by checking the existing tasks, then suggest any that are missing."
        )

        for turn in range(max_turns):
            if done:
                break

            log.info("Agentic loop turn %d/%d", turn + 1, max_turns)

            # Find all function-call parts in the response
            fc_parts = [
                p for p in response.candidates[0].content.parts
                if p.function_call is not None
            ]

            if not fc_parts:
                log.info("No function calls in response — agent finished naturally")
                break

            tool_response_parts = []
            for part in fc_parts:
                fc = part.function_call
                tool_name = fc.name
                tool_args = dict(fc.args)
                log.info("Tool call: %s | args: %s", tool_name, tool_args)

                result: dict
                if tool_name == "get_existing_tasks":
                    result = {
                        "existing_tasks": existing_task_names,
                        "existing_task_details": [
                            {
                                "task_type": t.task_type,
                                "name": t.name,
                                "duration_minutes": t.duration_minutes,
                                "frequency": t.frequency,
                                "preferred_time_windows": t.preferred_time_windows,
                            }
                            for t in existing_tasks
                        ],
                    }

                elif tool_name == "suggest_task":
                    proposed_name = str(tool_args["name"])
                    proposed_type = str(tool_args["task_type"])
                    proposed_frequency = str(tool_args["frequency"])
                    proposed_time_of_day = _extract_time_of_day(proposed_name)

                    preferred_windows = list(tool_args.get("preferred_time_windows", []))
                    if proposed_frequency == "twice_daily" and proposed_time_of_day:
                        log.info(
                            "Normalising inconsistent recurrence for '%s': twice_daily -> daily",
                            proposed_name,
                        )
                        proposed_frequency = "daily"
                        if preferred_windows:
                            if proposed_time_of_day in {"evening", "night"}:
                                preferred_windows = [preferred_windows[-1]]
                            else:
                                preferred_windows = [preferred_windows[0]]

                    proposed_name_key = _normalize_name(proposed_name)
                    proposed_canonical_key = _canonical_task_key(proposed_type, proposed_name)
                    suggested_name_keys = {_normalize_name(t.name) for t in suggested_tasks}
                    suggested_canonical_keys = {
                        _canonical_task_key(t.task_type, t.name) for t in suggested_tasks
                    }

                    if (
                        proposed_name_key in existing_name_keys
                        or proposed_name_key in suggested_name_keys
                    ):
                        log.info("Skipping duplicate task name: %s", proposed_name)
                        result = {"status": "skipped", "reason": "task already exists"}
                    elif (
                        proposed_canonical_key in existing_canonical_keys
                        or proposed_canonical_key in suggested_canonical_keys
                    ):
                        log.info(
                            "Skipping duplicate task intent: %s (%s)",
                            proposed_name,
                            proposed_canonical_key,
                        )
                        result = {
                            "status": "skipped",
                            "reason": "task intent already covered by existing schedule",
                        }
                    else:
                        task = CareTask(
                            task_type=proposed_type,
                            name=proposed_name,
                            duration_minutes=int(tool_args["duration_minutes"]),
                            priority=int(tool_args["priority"]),
                            frequency=proposed_frequency,
                            preferred_time_windows=preferred_windows,
                            is_time_flexible=bool(tool_args.get("is_time_flexible", True)),
                            notes=tool_args.get("notes", ""),
                            pet_name=pet.name,
                        )
                        suggested_tasks.append(task)
                        log.info("Suggested task: %s (priority %d)", task.name, task.priority)
                        result = {"status": "added", "task_name": task.name}

                elif tool_name == "finalize_plan":
                    explanation = tool_args.get("explanation", "")
                    log.info("Agent finalised plan with %d task(s)", len(suggested_tasks))
                    result = {"status": "finalized"}
                    done = True

                else:
                    log.warning("Unknown tool called: %s", tool_name)
                    result = {"error": f"Unknown tool: {tool_name}"}

                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": json.dumps(result)},
                    )
                )

            if done:
                break

            response = _send_message_with_retry(chat, tool_response_parts)

        if not done:
            log.warning("Agent did not call finalize_plan before the turn cap was reached")

    except genai_errors.ClientError as exc:
        log.exception("Gemini client error (code %s): %s", exc.code, exc)
        if exc.code == 429:
            msg = str(exc).lower()
            if "exceeded your current quota" in msg or "check your plan and billing" in msg:
                return {
                    "tasks": [],
                    "explanation": "",
                    "error": (
                        "Gemini API quota is exhausted for this key/project. "
                        "Enable billing or increase quota in Google AI Studio, then try again."
                    ),
                }
            return {
                "tasks": [],
                "explanation": "",
                "error": "Gemini rate limit reached. Wait a moment and try again.",
            }
        if exc.code in (401, 403):
            return {
                "tasks": [],
                "explanation": "",
                "error": "Invalid or unauthorised GOOGLE_API_KEY. Check that the key is correct and active.",
            }
        return {
            "tasks": [],
            "explanation": "",
            "error": f"API error ({exc.code}): {exc}",
        }
    except genai_errors.ServerError as exc:
        log.exception("Gemini server error: %s", exc)
        return {
            "tasks": [],
            "explanation": "",
            "error": "Gemini server error. Please try again in a moment.",
        }

    return {
        "tasks": suggested_tasks,
        "explanation": explanation,
        "error": None,
    }
