import uuid
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MEMORY_DB = BASE_DIR / "memory_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
chroma = chromadb.PersistentClient(path=str(MEMORY_DB))
collection = chroma.get_or_create_collection(name="agent_memory_bge")


def create_embedding(text: str) -> list[float]:
    return embedding_model.embed_query(text)


def list_memories() -> list[dict]:
    if collection.count() == 0:
        return []

    result = collection.get(include=["documents", "metadatas"])
    return [
        {"id": memory_id, "text": document, "metadata": metadata or {}}
        for memory_id, document, metadata in zip(
            result["ids"], result["documents"], result["metadatas"]
        )
    ]


def create_memory(text: str) -> str:
    memory_id = str(uuid.uuid4())
    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[create_embedding(text)],
        metadatas=[{"kind": "user_fact"}],
    )
    return memory_id


def update_memory(memory_id: str, text: str) -> str:
    collection.update(
        ids=[memory_id],
        documents=[text],
        embeddings=[create_embedding(text)],
        metadatas=[{"kind": "user_fact"}],
    )
    return memory_id


def delete_memory(memory_id: str) -> bool:
    if not any(memory["id"] == memory_id for memory in list_memories()):
        return False
    collection.delete(ids=[memory_id])
    return True


def search_memory(query: str, n_results: int = 5) -> list[dict]:
    if collection.count() == 0:
        return []

    result = collection.query(
        query_embeddings=[create_embedding(query)],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "id": memory_id,
            "text": document,
            "metadata": metadata or {},
            "distance": distance,
        }
        for memory_id, document, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
