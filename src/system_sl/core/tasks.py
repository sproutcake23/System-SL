import json
import random
import os
from datetime import datetime
import platform


from system_sl.utils import get_tasks_file_path
from system_sl.utils import load_data, save_data


TASKS_FILE_PATH = get_tasks_file_path("tasks.json")
COMPLETED_TASKS_FILE_PATH = get_tasks_file_path("completed_tasks.json")

def load_tasks():
    """Fetches active tasks from storage and automatically processes system migrations for legacy string formats.

    Returns:
        dict: A dictionary of categorized task objects containing title, created_at, and deadline fields.
    """
    data = load_data(TASKS_FILE_PATH)
    new_data = []
    if isinstance(data, dict):
        migrated = False
        for category, task_list in data.items():
            for task in task_list:
                if isinstance(task, str):
                    new_data.append(
                        {
                            "title": task,
                            "created_at": datetime.now().isoformat(),
                            "deadline": None,
                            "rank" : category
                        }
                    )
                    migrated = True
                else:
                    new_data.append(task)
            data = new_data

        if migrated:
            save_tasks(new_data)
    return data


def save_tasks(tasks: dict):
    """Persists active tasks directly to the main tracking database file.

    Args:
        tasks (dict): Categorized active dictionary data structure to write.

    Returns:
        None
    """
    save_data(TASKS_FILE_PATH, tasks)


def add_tasks( task_title: str ,task_type: str = "none", deadline: str = None):
    """Registers a new task inside a specific category pool while enforcing validation rules and avoiding duplicates.

    Args:
        task_type (str): The bucket name representing the task category.
        task_title (str): Summary description of the item to add.
        deadline (str, optional): Targeted deadline timestamp. Defaults to None.

    Returns:
        str: The sanitized task title string that was successfully saved.
    """
    # if not isinstance(task_type, str) or not task_type.strip():
    #     raise ValueError("Task type must be a non-empty string")

    if not isinstance(task_title, str) or not task_title.strip():
        raise ValueError("Task title must be a non-empty string")

    tasks = load_tasks()

    task_title = task_title.strip()

    # if task_type not in tasks:
    #     tasks[task_type] = []

    for task in tasks:
        if task["title"] == task_title:
            if deadline and task.get("deadline") != deadline:
                task["deadline"] = deadline
                save_tasks(tasks)

                print(f"Updated deadline for '{task_title}' to {deadline}")
                return task_title

            raise ValueError(f"Task '{task_title}' already exists in {task_type}")

    if isinstance(task_type, str):
        task_type = task_type.lower().strip()
    else:
        task_type = "None"

    new_task = {
        "title": task_title,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "deadline": deadline,
        "rank": task_type
    }

    tasks.append(new_task)
    save_tasks(tasks)
    return task_title


def remove_tasks(task_title: str, task_type: str = "none"):
    """Evicts a target task from active tracking files, popping the category if left empty.

    Args:
        task_type (str): The category container where the task resides.
        task_title (str): The exact text name of the task item to clean up.

    Returns:
        str: The title string of the successfully removed task.
    """
    if not isinstance(task_title, str) or not task_title.strip():
        raise ValueError("Task title must be a non-empty string")

    tasks = load_tasks()
    task_type = task_type.lower().strip()
    task_title = task_title.strip()

    # if task_type not in tasks:
    #     raise ValueError(f"Category {task_type} does not exist")

    original_count = len(tasks)

    tasks = [t for t in tasks if t["title"] != task_title]

    if len(tasks) == original_count:
        raise ValueError(f"Task '{task_title}' not found")

    # if not tasks[task_type]:
    #     tasks.pop(task_type)

    save_tasks(tasks)
    return task_title


def get_random_task():
    """Picks an outstanding item completely at random across all non-empty active categories.

    Returns:
        tuple[str, str] or None: A tuple mapping (category, task_title) if items exist, otherwise None.
    """
    tasks = load_tasks()
    # non_empty_cat = {k: v for k, v in tasks.items() if v}
    # if not non_empty_cat:
    #     return None
    # cat_key, cat_value = random.choice(list(non_empty_cat.items()))
    rand_task_obj = random.choice(tasks)

    return rand_task_obj["title"]


def load_completed_tasks():
    # """Fetches the complete historical array of items archived as completed.

    # Returns:
    #     dict: Parsed collection map containing log strings of finished events.
    # """
    """Fetches active tasks from storage and automatically processes system migrations for legacy string formats.

    Returns:
        dict: A dictionary of categorized task objects containing title, created_at, and deadline fields.
    """
    data = load_data(COMPLETED_TASKS_FILE_PATH)
    new_data = []
    if isinstance(data, dict):
        migrated = False
        for category, task_list in data.items():
            for task in task_list:
                if isinstance(task, str):
                    new_data.append(
                        {
                            "title": task,
                            "created_at": datetime.now().isoformat(),
                            "deadline": None,
                            "rank" : category
                        }
                    )
                    migrated = True
                else:
                    new_data.append(task)
            data = new_data

        if migrated:
            save_tasks(new_data)
    return data



def save_completed_tasks(tasks: dict):
    """Persists historical completion statistics changes directly onto file records.

    Args:
        tasks (dict): Updated logs structure tracking archived items.

    Returns:
        None
    """
    save_data(COMPLETED_TASKS_FILE_PATH, tasks)


def mark_task_completed(task_title: str, task_type: str = "none"):
    """Extracts a task out of active runtime arrays and logs it as completed inside history archives.

    Args:
        task_type (str): Original classification bucket tracking the item.
        task_title (str): Unique text identity of the task being checked off.

    Returns:
        str: The title of the validated task moved to historical logs.
    """
    removed_title = remove_tasks(task_title, task_type)

    completed_tasks = load_completed_tasks()
    # if task_type not in completed_tasks:
    #     completed_tasks[task_type] = []

    completion_entry = {
        "title": task_title,
        "Completed": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    if completion_entry not in completed_tasks:
        completed_tasks.append(completion_entry)

    save_completed_tasks(completed_tasks)
    return removed_title

if  __name__ == "__main__":
    print(mark_task_completed("Neggggg"))
 