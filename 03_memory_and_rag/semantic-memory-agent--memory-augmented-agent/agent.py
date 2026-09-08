from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from memory import create_memory, delete_memory, search_memory, update_memory


load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)


class MemoryAction(BaseModel):
    action: Literal["CREATE", "UPDATE", "DELETE", "IGNORE"] = Field(
        description="Lifecycle operation to apply to user memory"
    )
    memory: str = Field(
        default="",
        description="New or replacement memory text"
    )
    target_id: str = Field(
        default="",
        description="Existing memory ID for UPDATE or DELETE"
    )


def decide_memory_action(user_message: str) -> MemoryAction:
    candidates = search_memory(user_message, n_results=5)
    candidate_text = "\n".join(
        f"ID: {item['id']} | Memory: {item['text']}"
        for item in candidates
    ) or "No similar memories found."

    prompt = f"""
Decide how to manage long-term memory for this user message.

User message:
{user_message}

Similar existing memories:
{candidate_text}

Rules:
- CREATE: stable, useful new fact with no matching memory.
- UPDATE: the message changes or corrects an existing fact; use its ID.
- DELETE: the user clearly asks to forget an existing fact; use its ID.
- IGNORE: temporary requests, questions, secrets, or duplicate information.
- Never store passwords, API keys, or highly sensitive personal data.
- For UPDATE, memory must contain the complete replacement fact.
- For DELETE and IGNORE, return an empty memory string.
"""
    decision_model = llm.with_structured_output(MemoryAction)
    return decision_model.invoke([HumanMessage(content=prompt)])


def apply_memory_action(action: MemoryAction) -> str:
    if action.action == "CREATE" and action.memory:
        return f"created:{create_memory(action.memory)}"
    if action.action == "UPDATE" and action.target_id and action.memory:
        return f"updated:{update_memory(action.target_id, action.memory)}"
    if action.action == "DELETE" and action.target_id:
        return "deleted" if delete_memory(action.target_id) else "not_found"
    return "ignored"


def retrieve_memory(user_message: str) -> str:
    memories = search_memory(user_message, n_results=5)
    if not memories:
        return "No relevant memories found."
    return "\n".join(f"- {item['text']}" for item in memories)


def generate_answer(user_message: str, memories: str) -> str:
    prompt = f"""
You are an AI assistant.

Relevant memories:
{memories}

Current user message:
{user_message}

Use memories only when relevant. Do not mention the memory database.
Answer naturally.
"""
    return llm.invoke([HumanMessage(content=prompt)]).content
