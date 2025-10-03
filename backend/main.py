from fastapi import FastAPI, Path, HTTPException,Query
from pathlib import Path as FilePath
import json
import random

app = FastAPI(title="SL backend")

def load_json(file_name: str):
    path = FilePath(file_name)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get('/get_tasks/{task_type}')
def view_tasks(
        task_type: str = Path(..., description='Enter the type of the task', example='work'),
        random_pick: bool = Query(False, description='Return one random task if true')
):
    tasks = load_json("tasks.json")
    if task_type not in tasks:
        raise HTTPException(status_code=404, detail="task type not found")

    task_list = tasks[task_type]

    return random.choice(task_list) if random_pick else task_list

@app.get('/about')
def about():
    return {
        'message': 'This Application tries to bring the SYSTEM from the anime Solo Leveling into Real Life'
    }
