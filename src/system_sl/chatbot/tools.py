import json
from typing import Any, Callable

from core.tasks import (
    add_tasks,
    get_random_task,
    get_tasks_file_path,
    load_completed_tasks,
    load_data,
    load_tasks,
    mark_task_completed,
    remove_tasks,
)


TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "load_tasks",
            "description": (
                "Return the user's current open tasks, grouped by category. "
                "Each task has title, created_at, and deadline (may be null)."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_completed_tasks",
            "description": (
                "Return the user's completed tasks, grouped by category. "
                "Each entry is a string like 'title (Completed: YYYY-MM-DD)'."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": (
                "Add a new task. Returns the title on success, or "
                "{error: 'duplicate'} if a task with the same title exists in that category."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Lowercase category, e.g. 'work', 'study'.",
                    },
                    "title": {"type": "string", "description": "Task title."},
                    "deadline": {
                        "type": ["string", "null"],
                        "description": "Optional deadline 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'. null if unset.",
                    },
                },
                "required": ["category", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_task",
            "description": "Remove a task from a category. Returns the title on success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "title": {"type": "string"},
                },
                "required": ["category", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_completed",
            "description": "Move a task from open to completed. Returns the title on success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "title": {"type": "string"},
                },
                "required": ["category", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_task",
            "description": "Pick a random open task. Returns [category, title] or null when no tasks.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_persona",
            "description": (
                "Read the user's persona.json (10-question onboarding output). "
                "Returns the full document or {} if missing."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_user_info",
            "description": (
                "Read user_info.json (legacy goal keywords). "
                "Returns the full document or {} if missing."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _add_task(category: str, title: str, deadline: str | None = None) -> Any:
    try:
        return add_tasks(category, title, deadline)
    except ValueError as e:
        msg = str(e)
        kind = "duplicate" if "already exists" in msg else "invalid"
        return {"error": kind, "message": msg}


def _remove_task(category: str, title: str) -> Any:
    try:
        return remove_tasks(category, title)
    except ValueError as e:
        return {"error": "not_found", "message": str(e)}


def _mark_task_completed(category: str, title: str) -> Any:
    try:
        return mark_task_completed(category, title)
    except ValueError as e:
        return {"error": "not_found", "message": str(e)}


def _read_persona() -> Any:
    return load_data(get_tasks_file_path("persona.json"))


def _read_user_info() -> Any:
    return load_data(get_tasks_file_path("user_info.json"))


TOOL_DISPATCH: dict[str, Callable[..., Any]] = {
    "load_tasks": load_tasks,
    "load_completed_tasks": load_completed_tasks,
    "add_task": _add_task,
    "remove_task": _remove_task,
    "mark_task_completed": _mark_task_completed,
    "get_random_task": get_random_task,
    "read_persona": _read_persona,
    "read_user_info": _read_user_info,
}


def call_tool(name: str, arguments: dict | None) -> str:
    if name not in TOOL_DISPATCH:
        return json.dumps({"error": "unknown_tool", "name": name})

    fn = TOOL_DISPATCH[name]
    try:
        result = fn(**(arguments or {}))
    except TypeError as e:
        return json.dumps({"error": "bad_arguments", "message": str(e)})
    except Exception as e:
        return json.dumps({"error": "exception", "message": str(e)})

    try:
        return json.dumps(result, default=str)
    except (TypeError, ValueError):
        return json.dumps({"result": repr(result)})
