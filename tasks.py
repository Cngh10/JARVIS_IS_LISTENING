import time

TASKS = []


def add_task(text, trigger_time):
    TASKS.append({
        "text": text,
        "time": trigger_time,
        "done": False
    })


def check_tasks():
    current = time.time()
    ready = []

    for task in TASKS:
        if not task["done"] and current >= task["time"]:
            ready.append(task)
            task["done"] = True

    return ready