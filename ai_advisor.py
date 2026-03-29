"""
PawPal+ AI Care Advisor
Agentic workflow powered by Claude with tool use.

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
   Tool results are fed back as user messages so the model can observe the
   outcome of each action and adjust (standard agentic pattern).
"""

from __future__ import annotations

import json
import logging
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()  # load ANTHROPIC_API_KEY from .env if present

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
1. Call `get_existing_tasks` first to see what tasks are already scheduled.
2. Call `suggest_task` for each new task that is genuinely relevant and not \
   already covered.
3. Call `finalize_plan` once with a concise explanation of your recommendations \
   and the reasoning behind each one.

Rules:
- Only suggest tasks relevant to this specific pet's profile and conditions.
- Do NOT suggest tasks whose names are already in the existing task list.
- Prioritise medical/medication tasks (priority 4–5) and time-critical tasks \
  (is_time_flexible=False).
- Be specific: use durations and time windows consistent with the guidelines.
- Suggest no more than 7 tasks total.
- If the existing tasks already cover the pet's needs well, suggest nothing \
  new and explain that in finalize_plan.
"""


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[dict] = [
    {
        "name": "get_existing_tasks",
        "description": "Returns the names of care tasks already added for this pet.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "suggest_task",
        "description": "Suggests a new care task to add to the pet's schedule.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_type": {
                    "type": "string",
                    "enum": ["walk", "feed", "medication", "grooming",
                             "enrichment", "training", "health_check"],
                    "description": "Category of care task.",
                },
                "name": {
                    "type": "string",
                    "description": "Short descriptive task name.",
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "How long the task takes in minutes.",
                },
                "priority": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "1=low importance, 5=critical.",
                },
                "frequency": {
                    "type": "string",
                    "enum": ["daily", "twice_daily", "weekly"],
                    "description": "How often the task recurs.",
                },
                "preferred_time_windows": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional HH:MM-HH:MM windows. Provide 2 for twice_daily tasks "
                        "(AM window first, then PM window)."
                    ),
                },
                "is_time_flexible": {
                    "type": "boolean",
                    "description": (
                        "Set False for tasks that must happen at the specified time "
                        "(e.g. medication, insulin). Defaults to True."
                    ),
                },
                "notes": {
                    "type": "string",
                    "description": "Optional care instruction or context for the owner.",
                },
            },
            "required": ["task_type", "name", "duration_minutes", "priority", "frequency"],
        },
    },
    {
        "name": "finalize_plan",
        "description": (
            "Call this when you have finished suggesting tasks. "
            "Provide a summary of what was recommended and why."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "explanation": {
                    "type": "string",
                    "description": (
                        "Natural language explanation of the suggested tasks and the "
                        "reasoning behind each recommendation."
                    ),
                },
            },
            "required": ["explanation"],
        },
    },
]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_ai_advisor(
    pet: Pet,
    existing_task_names: list[str],
) -> dict:
    """Run the agentic care advisor for *pet*.

    Parameters
    ----------
    pet:
        The Pet object whose profile drives retrieval and suggestions.
    existing_task_names:
        Names of tasks already on the pet's schedule (used to avoid duplicates).

    Returns
    -------
    dict with keys:
        tasks       – list[CareTask] suggested by the agent
        explanation – agent's natural-language reasoning string
        error       – str if something went wrong, else None
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        log.error("ANTHROPIC_API_KEY is not set")
        return {
            "tasks": [],
            "explanation": "",
            "error": (
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Add it to a .env file (see .env.example) or export it in your shell."
            ),
        }

    client = anthropic.Anthropic(api_key=api_key)

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

    messages: list[dict] = [
        {
            "role": "user",
            "content": (
                f"Please suggest a personalised care plan for {pet.name}. "
                "Start by checking the existing tasks, then suggest any that are missing."
            ),
        }
    ]

    suggested_tasks: list[CareTask] = []
    explanation = ""
    done = False
    max_turns = 15  # safety cap on agentic loop iterations

    try:
        for turn in range(max_turns):
            if done:
                break

            log.info("Agentic loop turn %d/%d", turn + 1, max_turns)
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=2048,
                system=system_prompt,
                tools=TOOLS,
                messages=messages,
            )
            log.info("stop_reason=%s", response.stop_reason)

            # Append assistant turn to history
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                break
            if response.stop_reason != "tool_use":
                log.warning("Unexpected stop_reason: %s — ending loop", response.stop_reason)
                break

            # Process tool calls and build result list
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                log.info("Tool call: %s | input: %s", block.name, block.input)
                result: dict
                if block.name == "get_existing_tasks":
                    result = {"existing_tasks": existing_task_names}

                elif block.name == "suggest_task":
                    inp = block.input
                    # Deduplicate: skip if the name is already present
                    if inp["name"] in existing_task_names or any(
                        t.name == inp["name"] for t in suggested_tasks
                    ):
                        log.info("Skipping duplicate task: %s", inp["name"])
                        result = {"status": "skipped", "reason": "task already exists"}
                    else:
                        task = CareTask(
                            task_type=inp["task_type"],
                            name=inp["name"],
                            duration_minutes=inp["duration_minutes"],
                            priority=inp["priority"],
                            frequency=inp["frequency"],
                            preferred_time_windows=inp.get("preferred_time_windows", []),
                            is_time_flexible=inp.get("is_time_flexible", True),
                            notes=inp.get("notes", ""),
                            pet_name=pet.name,
                        )
                        suggested_tasks.append(task)
                        log.info("Suggested task: %s (priority %d)", task.name, task.priority)
                        result = {"status": "added", "task_name": task.name}

                elif block.name == "finalize_plan":
                    explanation = block.input.get("explanation", "")
                    log.info("Agent finalised plan with %d task(s)", len(suggested_tasks))
                    result = {"status": "finalized"}
                    done = True

                else:
                    log.warning("Unknown tool called: %s", block.name)
                    result = {"error": f"Unknown tool: {block.name}"}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

        if not done:
            log.warning("Agent did not call finalize_plan before the turn cap was reached")

    except anthropic.AuthenticationError:
        log.exception("Invalid API key")
        return {
            "tasks": [],
            "explanation": "",
            "error": "Invalid ANTHROPIC_API_KEY. Check that the key is correct and active.",
        }
    except anthropic.RateLimitError:
        log.exception("Rate limit hit")
        return {
            "tasks": [],
            "explanation": "",
            "error": "Anthropic rate limit reached. Wait a moment and try again.",
        }
    except anthropic.APIError as exc:
        log.exception("Anthropic API error: %s", exc)
        return {
            "tasks": [],
            "explanation": "",
            "error": f"API error: {exc}",
        }

    return {
        "tasks": suggested_tasks,
        "explanation": explanation,
        "error": None,
    }
