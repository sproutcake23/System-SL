from fastapi import FastAPI
import json
import random

app = FastAPI(title="SL backend")

with open("tasks.json", "r") as f:
    TASKS = json.load(f)

@app.get("/tasks")
def get_random_task():
    return {"task": random.choice(TASKS)}