import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def remember(key, value):
    data = load_memory()
    data[key] = value
    save_memory(data)


def recall(key):
    data = load_memory()
    return data.get(key, None)


def get_all_memory():
    return load_memory()