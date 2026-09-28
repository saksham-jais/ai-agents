from config import structured_invoke
from models import CodeArtifact, ReviewReport


def reviewer_agent(task: str, artifact: CodeArtifact) -> ReviewReport:
    review_files = {
        filename: content[:6000]
        for filename, content in artifact.files.items()
    }

    prompt = f"""
You are a senior software engineer reviewing code.

Original task:
{task}

Review the following implementation:

{review_files}

Look for:

1. Bugs
2. Security issues
3. Poor architecture
4. Missing error handling
5. Incorrect assumptions
6. Maintainability problems
7. Performance problems

Return a structured review. Set approved to true only when no critical or
high-severity issues remain.
"""

    return structured_invoke(ReviewReport, prompt)