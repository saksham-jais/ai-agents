from config import structured_invoke
from pydantic import BaseModel
from web_search import search_web


class ResearchResult(BaseModel):
    findings: str


def researcher_agent(task: str, memory_context: str = "") -> str:

    prompt = f"""
You are the Research Agent.

Your responsibility is to research technical
information needed to complete a software project.

Task:

{task}

Use your technical knowledge and clearly identify information that should
be verified against current official documentation.

Relevant lessons from earlier projects:
{memory_context or "No earlier project lessons found."}

Live search results:
{search_web(task)}

Focus on:
- official documentation
- current best practices
- technical constraints
- useful libraries
- architecture considerations

Return concise technical findings.
"""

    return structured_invoke(ResearchResult, prompt).findings