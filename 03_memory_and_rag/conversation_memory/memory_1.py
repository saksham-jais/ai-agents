import json
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parent / "memory.json"


def load_memories():
    if not MEMORY_FILE.exists():
        return []

    with MEMORY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_memories(memories):
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(memories, file, indent=2, ensure_ascii=False)


def add_memory(memory):
    memory = memory.strip()
    if not memory:
        return False

    memories = load_memories()

    if memory in memories:
        return False

    memories.append(memory)
    save_memories(memories)
    return True


def get_memories():
    return load_memories()