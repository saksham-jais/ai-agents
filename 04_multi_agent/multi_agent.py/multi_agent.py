import json
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

MAX_REVISIONS = 3


def invoke_with_retry(prompt: str, attempts: int = 3):
    last_error = None
    for attempt in range(attempts):
        try:
            return llm.invoke(prompt)
        except Exception as error:
            last_error = error
            if attempt < attempts - 1:
                is_rate_limit = "RateLimit" in type(error).__name__ or "429" in str(error)
                time.sleep(10 * (attempt + 1) if is_rate_limit else 2**attempt)
    raise RuntimeError(f"Model call failed after {attempts} attempts") from last_error


@dataclass
class TeamState:
    task: str
    code: str = ""
    feedback: str = ""
    review_status: str = "pending"
    revision_count: int = 0
    messages: list = field(default_factory=list)


def coder_agent(state: TeamState):
    """Generate or revise the implementation."""

    response = invoke_with_retry(f"""
You are a Python coding agent. Produce complete Python code. When given review
feedback, fix the reported issues. Return code only, without Markdown fences.

Task:
{state.task}

Previous implementation:
{state.code or "None"}

Reviewer feedback:
{state.feedback or "None"}
""")

    return response.content


def reviewer_agent(state: TeamState):
    """Review the code and return a structured verdict."""

    response = invoke_with_retry(f"""
You are a strict Python code reviewer. Check correctness, error handling and
security. Approve only if you find no significant issues.

Original task:
{state.task}

Implementation:
{state.code}

Return only valid JSON matching this schema:
{{
  "status": "approved" or "changes_requested",
  "feedback": "string"
}}
""")

    content = response.content.strip()
    if content.startswith("```"):
        content = content.removeprefix("```").removeprefix("json").strip()
        content = content.removesuffix("```").strip()
    return json.loads(content)


def supervisor(task: str):
    state = TeamState(task=task)

    while True:

        # HANDOFF: Supervisor -> Coder
        state.messages.append({
            "from": "supervisor",
            "to": "coder",
            "type": "assignment"
        })

        state.code = coder_agent(state)

        # HANDOFF: Coder -> Reviewer
        state.messages.append({
            "from": "coder",
            "to": "reviewer",
            "type": "review_request"
        })

        review = reviewer_agent(state)

        state.review_status = review["status"]
        state.feedback = review["feedback"]

        # Conditional routing
        if state.review_status == "approved":
            state.messages.append({
                "from": "reviewer",
                "to": "supervisor",
                "type": "approval"
            })
            break

        # Prevent infinite revision loops
        if state.revision_count >= MAX_REVISIONS:
            state.review_status = "needs_human_review"
            break

        state.revision_count += 1

        # HANDOFF: Reviewer -> Coder
        state.messages.append({
            "from": "reviewer",
            "to": "coder",
            "type": "revision_request",
            "feedback": state.feedback
        })

    return state


if __name__ == "__main__":
    task = input("Describe the coding task: ")

    result = supervisor(task)

    print("\nFINAL STATUS:", result.review_status)
    print("\nCODE:\n", result.code)
    print("\nREVIEW:\n", result.feedback)
    print("\nHANDOFF HISTORY:")

    for message in result.messages:
        print(message)