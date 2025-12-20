import json
import random
import os
from datetime import datetime


def get_tasks_file_path(filename):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(curr_dir))

    return os.path.join(project_root, "data", filename)


TASKS_FILE_PATH = get_tasks_file_path("tasks.json")
COMPLETED_TASKS_FILE_PATH = get_tasks_file_path("completed_tasks.json")


def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"File {os.path.basename(filepath)} not found. Creating it.")
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("{}")
            return {}
        except Exception as e:
            print(f"Could not create file {filepath}: {e}")
            return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read().strip()

            if not data:
                return {}

            return json.loads(data)
    except Exception as e:
        print(f"Error loading data {e}")
        return {}


def save_data(filepath, tasks: dict):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    except Exception as e:
        print(f"Could not save data to the file {filepath}: {e}")


def load_tasks():
    data = load_data(TASKS_FILE_PATH)

    migrated = False
    for category, task_list in data.items():
        new_list = []
        for task in task_list:
            if isinstance(task, str):
                new_list.append(
                    {
                        "title": task,
                        "created_at": datetime.now().isoformat(),
                        "deadline": None,
                    }
                )
                migrated = True
            else:
                new_list.append(task)
        data[category] = new_list

    if migrated:
        save_tasks(data)

    return data


def save_tasks(tasks: dict):
    save_data(TASKS_FILE_PATH, tasks)


def add_tasks(task_type: str, task_title: str, deadline: str = None):
    if not isinstance(task_type, str) or not task_type.strip():
        raise ValueError("Task type must be a non-empty string")

    if not isinstance(task_title, str) or not task_title.strip():
        raise ValueError("Task title must be a non-empty string")

    tasks = load_tasks()
    task_type = task_type.lower().strip()
    task_title = task_title.strip()

    if task_type not in tasks:
        tasks[task_type] = []

    for task in tasks[task_type]:
        if task["title"] == task_title:
            if deadline and task.get("deadline") != deadline:
                task["deadline"] = deadline
                save_tasks(tasks)

                print(f"Updated deadline for '{task_title}' to {deadline}")
                return task_title

            raise ValueError(f"Task '{task_title}' already exists in {task_type}")

    new_task = {
        "title": task_title,
        "created_at": datetime.now().isoformat(),
        "deadline": deadline,
    }

    tasks[task_type].append(new_task)
    save_tasks(tasks)
    return task_title


def remove_tasks(task_type: str, task_title: str):
    if not isinstance(task_type, str) or not task_type.strip():
        raise ValueError("Task type must be a non-empty string")

    if not isinstance(task_title, str) or not task_title.strip():
        raise ValueError("Task title must be a non-empty string")

    tasks = load_tasks()
    task_type = task_type.lower().strip()
    task_title = task_title.strip()

    if task_type not in tasks:
        raise ValueError(f"Category {task_type} does not exist")

    original_count = len(tasks[task_type])

    tasks[task_type] = [t for t in tasks[task_type] if t["title"] != task_title]

    if len(tasks[task_type]) == original_count:
        raise ValueError(f"Task '{task_title}' not found in {task_type}")

    if not tasks[task_type]:
        tasks.pop(task_type)

    save_tasks(tasks)
    return task_title


def get_random_task():
    tasks = load_tasks()
    non_empty_cat = {k: v for k, v in tasks.items() if v}
    if not non_empty_cat:
        return None
    cat_key, cat_value = random.choice(list(non_empty_cat.items()))
    rand_task_obj = random.choice(cat_value)

    return cat_key, rand_task_obj["title"]


def load_completed_tasks():
    return load_data(COMPLETED_TASKS_FILE_PATH)


def save_completed_tasks(tasks: dict):
    save_data(COMPLETED_TASKS_FILE_PATH, tasks)


def mark_task_completed(task_type: str, task_title: str):
    removed_title = remove_tasks(task_type, task_title)

    completed_tasks = load_completed_tasks()
    if task_type not in completed_tasks:
        completed_tasks[task_type] = []

    completion_entry = (
        f"{task_title} (Completed: {datetime.now().strftime('%Y-%m-%d')})"
    )

    if completion_entry not in completed_tasks[task_type]:
        completed_tasks[task_type].append(completion_entry)

    save_completed_tasks(completed_tasks)
    return removed_title
