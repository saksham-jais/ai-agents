import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)


async def invoke_with_retry(prompt, attempts=3):
    last_error = None

    for attempt in range(attempts):
        try:
            return await llm.ainvoke(prompt)
        except Exception as error:
            last_error = error
            if attempt < attempts - 1:
                is_rate_limit = "RateLimit" in type(error).__name__ or "429" in str(error)
                await asyncio.sleep(10 * (attempt + 1) if is_rate_limit else 2**attempt)

    raise RuntimeError(f"Model call failed after {attempts} attempts") from last_error


async def security_agent(code):

    response = await invoke_with_retry(f"""
You are a security reviewer.

Analyze this code for:

- security vulnerabilities
- unsafe input handling
- injection risks
- authentication/authorization issues
- sensitive data exposure

Code:

{code}

Return concise findings.
"""
    )

    return {
        "agent": "security",
        "result": response.content
    }


async def performance_agent(code):

    response = await invoke_with_retry(f"""
You are a performance engineer.

Analyze this code for:

- unnecessary computation
- inefficient algorithms
- database/API bottlenecks
- memory problems
- scalability issues

Code:

{code}

Return concise findings.
"""
    )

    return {
        "agent": "performance",
        "result": response.content
    }


async def architecture_agent(code):

    response = await invoke_with_retry(f"""
You are a software architect.

Analyze this code for:

- architecture problems
- maintainability
- separation of concerns
- coupling
- extensibility
- design problems

Code:

{code}

Return concise findings.
"""
    )

    return {
        "agent": "architecture",
        "result": response.content
    }


async def synthesis_agent(code, results):
    findings = "\n\n".join(
        f"{item['agent'].upper()} REVIEW:\n{item['result']}"
        for item in results
    )

    response = await invoke_with_retry(f"""
You are the lead engineer synthesizing a code review.

Review the original code and the specialist findings below. Produce a concise,
actionable final engineering review. Group related findings and identify the
highest-priority fixes. Do not invent issues that are not supported by the
specialist reviews.

Original code:
{code}

Specialist findings:
{findings}
""")

    return response.content