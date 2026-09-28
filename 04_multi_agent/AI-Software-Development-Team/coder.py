import re

from config import invoke_with_retry, llm
from models import CodeArtifact


def coder_agent(
    task: str,
    research: str,
    previous_code: CodeArtifact | None = None,
    review_feedback: str = "",
) -> CodeArtifact:

    prompt = f"""
You are the Coding Agent.

Your responsibility is to write high-quality Python code.

User requirement:

{task}

Research provided by the Research Agent:

{research}

Create the implementation.

Requirements:

- clean architecture
- readable code
- error handling
- reasonable project structure
- explain important decisions

Return source files using exactly this format for every file:
FILE: relative/path.py
```python
file contents
```
Include tests when appropriate. Do not return JSON.

Previous implementation:
{previous_code.model_dump_json(indent=2) if previous_code else "None"}

Reviewer feedback to address:
{review_feedback or "None"}
"""

    response = invoke_with_retry(lambda: llm.invoke(prompt))

    def parse_files(content: str) -> list[tuple[str, str]]:
        matches = re.findall(
            r"(?ms)^FILE:\s*(?P<name>[^\s]+)\s*\n```[^\n]*\n(?P<content>.*?)\n```",
            content,
        )
        if not matches:
            matches = re.findall(
                r"(?ms)^(?:#+\s*)?(?P<name>[\w./-]+\.py)\s*\n```[^\n]*\n(?P<content>.*?)\n```",
                content,
            )
        if not matches:
            blocks = re.findall(r"(?ms)```(?:python|py)?\s*\n(?P<content>.*?)\n```", content)
            matches = [("main.py", blocks[0])] if len(blocks) == 1 else []
        return matches

    matches = parse_files(response.content)
    if not matches:
        repair_prompt = f"""Create the implementation for this task: {task}
Return ONLY one Python file using this exact format:
FILE: main.py
```python
complete runnable code
```
No explanation, no JSON, and no additional text."""
        repair_response = invoke_with_retry(lambda: llm.invoke(repair_prompt))
        matches = parse_files(repair_response.content)
    if not matches:
        if previous_code is not None:
            return previous_code
        raise ValueError(
            "Coder did not return parseable source files. Response preview: "
            f"{response.content[:1000]}"
        )
    return CodeArtifact(
        files={name: content for name, content in matches},
        explanation="Generated and revised from research and reviewer feedback.",
    )