import json
import random
import os


def get_tasks_file_path():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(curr_dir))

    return os.path.join(project_root, "data", "tasks.json")


TASKS_FILE_PATH = get_tasks_file_path()


def load_tasks():
    if not os.path.exists(TASKS_FILE_PATH):
        print("tasks.json not found")
        try:
            print("Creating tasks.json")
            os.makedirs(os.path.dirname(TASKS_FILE_PATH), exist_ok=True)
            with open(TASKS_FILE_PATH, "w", encoding="utf-8") as f:
                f.write("{}")
            return {}
        except Exception as e:
            print(f"Could not create tasks file {e}")
            return {}
    try:
        with open(TASKS_FILE_PATH, "r", encoding="utf-8") as f:
            data = f.read().strip()

            if not data:
                return {}

            return json.loads(data)
    except Exception as e:
        print(f"Error loading data {e}")
        return {}


def save_tasks(tasks: dict):
    tasks_file_path = TASKS_FILE_PATH
    try:
        with open(tasks_file_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    except Exception as e:
        print(f"Could not save tasks to the file {e}")


def add_tasks(task_type: str, task_title: str):
    if not isinstance(task_type, str) or not task_type.strip():
        raise ValueError("Task type must be a non-empty string")

    if not isinstance(task_title, str) or not task_title.strip():
        raise ValueError("Task title must be a non-empty string")

    tasks = load_tasks()
    task_type = task_type.lower().strip()
    task_title = task_title.lower().strip()

    if task_type not in tasks:
        tasks[task_type] = []
        tasks[task_type].append(task_title)

    save_tasks(tasks)

    return task_title

def remove_tasks():
    pass  #pending

