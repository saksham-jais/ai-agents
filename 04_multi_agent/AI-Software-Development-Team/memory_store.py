import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import embedding_model


MEMORY_FILE = Path(__file__).resolve().parent / "team_memory.json"


def _read() -> list[dict]:
    if not MEMORY_FILE.exists():
        return []
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))


def _similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def remember(task: str, outcome: str) -> None:
    entries = _read()
    entries.append(
        {
            "id": str(uuid.uuid4()),
            "task": task,
            "outcome": outcome,
            "embedding": embedding_model.embed_query(task),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    MEMORY_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def search(query: str, limit: int = 3) -> list[dict]:
    entries = _read()
    if not entries:
        return []
    query_embedding = embedding_model.embed_query(query)
    ranked = sorted(
        entries,
        key=lambda item: _similarity(query_embedding, item["embedding"]),
        reverse=True,
    )
    return ranked[:limit]