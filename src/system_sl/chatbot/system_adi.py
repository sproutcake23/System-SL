from typing import Any, Optional
from functools import lru_cache

# LangChain / Google Imports
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Assuming these are imported from your core module as before
from system_sl.core import (
    add_tasks,
    remove_tasks,
    mark_task_completed as core_mark_task_completed,
    load_tasks as core_load_tasks,
    load_completed_tasks as core_load_completed_tasks,
    get_random_task as core_get_random_task,
)

from system_sl.utils import (
    load_data,
    get_tasks_file_path,
)

from system_sl.chatbot import FRIEND_PROMPT, SYSTEM_MENTOR_PROMPT


@tool
def load_tasks() -> Any:
    """
    Return the user's current open tasks, grouped by category.

    When to use:
    Use this tool whenever the user asks to see what tasks they need to do,
    wants a list of their current objectives, or checks their active progression status.

    Args:
        None

    Returns:
        Any: A structure containing all open tasks where each task contains a title,
             created_at timestamp, and an optional deadline.
    """
    # Placeholder for your core loading function
    return core_load_tasks()
    pass


@tool
def load_completed_tasks() -> Any:
    """
    Return the user's historical completed tasks, grouped by category.

    When to use:
    Use this tool when the user asks about their achievements, past completed tasks,
    or historical records of what they have successfully finished.

    Args:
        None

    Returns:
        Any: A dictionary grouped by category containing strings like 'title (Completed: YYYY-MM-DD)'.
    """
    return core_load_completed_tasks()
    pass


@tool
def add_task(category: str, title: str, deadline: Optional[str] = None) -> Any:
    """
    Add a brand new task to a specific category.

    When to use:
    Use this tool when the user explicitly commands to add, create, or register
    a new task, goal, quest, or objective into their tracker.

    Args:
        category (str): The lowercase category string where the task belongs (e.g., 'work', 'study').
        title (str): The descriptive title text of the task.
        deadline (Optional[str]): Optional completion target date/time matching 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'. Defaults to None.

    Returns:
        Any: The string title on a successful creation, or a dictionary containing
             the error key (e.g., {"error": "duplicate"}) if it already exists.
    """
    try:
        return add_tasks(category, title, deadline)
    except ValueError as e:
        msg = str(e)
        kind = "duplicate" if "already exists" in msg else "invalid"
        return {"error": kind, "message": msg}


@tool
def remove_task(category: str, title: str) -> Any:
    """
    Remove/delete a specific task from a targeted category completely.

    When to use:
    Use this tool when the user wants to completely delete, drop, or cancel
    an existing task without completing it.

    Args:
        category (str): The category name where the task resides.
        title (str): The exact title text of the task to be removed.

    Returns:
        Any: The string title on a successful deletion, or a dictionary with
             an error key if the task wasn't found (e.g., {"error": "not_found"}).
    """
    try:
        return remove_tasks(category, title)
    except ValueError as e:
        return {"error": "not_found", "message": str(e)}


@tool
def mark_task_completed(category: str, title: str) -> Any:
    """
    Move a task from the open status to the completed status pool.

    When to use:
    Use this tool when the user claims they have completed, finished,
    cleared, or successfully executed a specific task objective.

    Args:
        category (str): The category name where the task resides.
        title (str): The exact title text of the task to mark complete.

    Returns:
        Any: The string title on a successful completion change, or a dictionary
             with an error key if the task doesn't exist (e.g., {"error": "not_found"}).
    """
    try:
        return core_mark_task_completed(category, title)
    except ValueError as e:
        return {"error": "not_found", "message": str(e)}


@tool
def get_random_task() -> Any:
    """
    Pick and select one random open task from the user's active categories.

    When to use:
    Use this tool when the user cannot decide what to do next, feels stuck,
    or explicitly asks the system to pick a random assignment/quest for them.

    Args:
        None

    Returns:
        Any: A list matching [category, title] if a task is found, or null/None if no tasks exist.
    """
    return core_get_random_task()
    pass


@tool
def read_persona() -> Any:
    """
    Read the user's personal archetype profile configuration (from onboarding metrics).

    When to use:
    Use this tool if you need deep historical insights about the user's core playstyle,
    motivation parameters, or personality constraints to tailor conversational traits.

    Args:
        None

    Returns:
        Any: The parsed JSON contents of the persona document file, or an empty dict `{}` if missing.
    """
    return load_data(get_tasks_file_path("persona.json"))


@tool
def read_user_info() -> Any:
    """
    Read the legacy user goals and behavioral keywords profile file.

    When to use:
    Use this tool if the user references long-term goals or keywords that aren't explicit
    in their active task board layout.

    Args:
        None

    Returns:
        Any: The parsed JSON context profile document, or an empty dict `{}` if missing.
    """
    return load_data(get_tasks_file_path("user_info.json"))


# To hand these off to your LangChain Agent Executor later, you simply group them in a list:
# tools = [load_tasks, load_completed_tasks, add_task, remove_task, mark_task_completed, get_random_task, read_persona, read_user_info]


# --- Lazy initialization ---------------------------------------------------
# The LLM and agents must NOT be instantiated at import time: LangChain /
# pydantic validate GOOGLE_API_KEY the moment ChatGoogleGenerativeAI is
# constructed, which happens before main() can prompt the user for a key.
# Instead, expose cached factory functions that build each object on first use
# (i.e. when a ChatSession is created) and reuse the same instance thereafter.


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    """Build (once) and return the shared Gemini chat model.

    Construction is deferred until the first call so that GOOGLE_API_KEY is
    already present in the environment by the time pydantic validates it.
    """
    return ChatGoogleGenerativeAI(
        model="models/gemma-4-31b-it",
        temperature=0,
    )


@lru_cache(maxsize=1)
def get_system_agent():
    """Build (once) and return the SYSTEM mentor agent."""
    return create_agent(
        model=get_llm(),
        tools=[
            load_tasks,
            load_completed_tasks,
            add_task,
            remove_task,
            mark_task_completed,
            get_random_task,
            read_persona,
            read_user_info,
        ],
        system_prompt=SYSTEM_MENTOR_PROMPT,
    )


@lru_cache(maxsize=1)
def get_adi_agent():
    """Build (once) and return the FRIEND (Adi) agent."""
    return create_agent(
        model=get_llm(),
        tools=[
            load_tasks,
            load_completed_tasks,
            get_random_task,
            read_persona,
            read_user_info,
        ],
        system_prompt=FRIEND_PROMPT,
    )


# Flexible printing for different LangChain message formats
# last_message = result["messages"][-1]
# if hasattr(last_message, 'content'):
#     print(last_message.content)
# else:
#     print(last_message)

