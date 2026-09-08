from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from memory_1 import add_memory, get_memories


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


class MemoryDecision(BaseModel):
    should_remember: bool = Field(
        description="Whether this message contains a useful long-term user fact"
    )
    memory: str = Field(
        description="One concise fact to store, or an empty string"
    )


def extract_memory(user_message):
    prompt = f"""
Analyze this user message:

{user_message}

Determine whether it contains information
that would be useful to remember about the user
in future conversations.

Examples of useful memory:

- stable preferences
- technical preferences
- ongoing projects
- recurring goals
- preferred tools
- communication preferences

Store information only when it is stable, specific, and likely to help in
future conversations. Do not store one-time questions, temporary task details,
secrets, passwords, API keys, or sensitive personal information. If a fact is
useful, rewrite it as one short statement about the user.
"""

    decision_model = llm.with_structured_output(MemoryDecision)
    # print(decision_model.invoke([HumanMessage(content=prompt)]))
    decision = decision_model.invoke(
        [HumanMessage(content=prompt)]
    )

    # print("\nMemory decision:")
    # print(decision)
    # print("Should remember:", decision.should_remember)
    # print("Memory:", decision.memory)

    return decision


def answer(user_message):
    memories = get_memories()

    memory_text = "\n".join(f"- {memory}" for memory in memories)
    if not memory_text:
        memory_text = "No stored memories."

    prompt = f"""
You are an AI assistant.

Relevant memories about the user:

{memory_text}

User message:

{user_message}

Use the memories only when relevant.

Answer the user naturally.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def remember_and_answer(user_message):
    decision = extract_memory(user_message)
    memory_saved = False

    if decision.should_remember and decision.memory:
        memory_saved = add_memory(decision.memory)

    return answer(user_message), decision, memory_saved