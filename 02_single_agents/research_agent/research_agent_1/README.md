# Research Agent 1

This project demonstrates a planner-worker-synthesizer research workflow.

A user provides one research topic. The planner breaks that topic into exactly three independent tasks. Three worker agents run those tasks in parallel. Each worker searches the web and analyzes its own results. Finally, the synthesizer combines the three analyses into one report and saves it as `research_report.md`.

## Architecture

```text
USER
  |
  v
main.py: research(topic)
  |
  v
planner.py: create_plan()
  |
  v
ResearchPlan with three ResearchTask objects
  |
  +------------------+------------------+
  |                  |                  |
  v                  v                  v
agent.py          agent.py          agent.py
run_task()        run_task()        run_task()
  |                  |                  |
  v                  v                  v
tools.py          tools.py          tools.py
web_search()      web_search()      web_search()
  |                  |                  |
  +------------------+------------------+
                     |
                     v
main.py: synthesize_report()
                     |
                     v
          research_report.md
```

## Folder Contents

```text
research_agent_1/
|
|-- README.md       This documentation
|-- main.py         Main coordinator and synthesizer
|-- planner.py      Structured research-plan creation
|-- agent.py        Logic for one worker agent
|-- tools.py        Web-search tool
|-- research_report.md  Generated report after a run
```

`research_report.md` is generated when the program runs. It is not required for the program to start.

## Requirements

The code uses:

- Python 3.10 or newer
- `langchain-core`
- `langchain-community`
- `langchain-groq`
- `pydantic`
- `python-dotenv`
- DuckDuckGo search support used by `DuckDuckGoSearchRun`

The project also requires a Groq API key. Put it in a `.env` file in the project root or another location loaded by your environment:

```env
GROQ_API_KEY=your_api_key_here
```

Do not commit the `.env` file or expose the API key in source code.

## Run the Agent

From the repository root:

```powershell
python .\02_single_agents\research_agent\research_agent_1\main.py
```

The program asks for a topic:

```text
What would you like to research? Compare LangGraph and CrewAI for building multi-agent systems.
```

The program then prints progress similar to:

```text
1. Planner: creating three tasks...
   Task 1: Fundamentals
   Task 2: Practical applications
   Task 3: Limitations and tradeoffs
2. Agents: running tasks in parallel...
3. Synthesizer: creating final report...
4. Report saved to D:\...\research_agent_1\research_report.md
```

The final report is printed to the terminal and saved in the same folder as `main.py`.

## How the Files Work

### `tools.py`

This file owns the external capability used by the worker agents.

```python
search_engine = DuckDuckGoSearchRun()
```

This creates a DuckDuckGo search client.

```python
@tool
def web_search(query: str) -> str:
    """Search the web and return relevant results for a research task."""
    return search_engine.invoke(query)
```

`web_search`:

1. Receives a query string.
2. Sends the query to DuckDuckGo.
3. Returns the search result text.
4. Uses LangChain's `@tool` decorator so it can be used as an agent tool.

Example call:

```python
from tools import web_search

results = web_search.invoke({"query": "What is LangGraph?"})
print(results)
```

The tool is deliberately kept separate from the agent logic. This makes it easier to replace DuckDuckGo with another search provider later.

### `planner.py`

This file creates a structured plan.

#### `ResearchTask`

```python
class ResearchTask(BaseModel):
    title: str
    query: str
```

One task contains:

- `title`: a readable task name
- `query`: a focused web-search query

Example:

```python
ResearchTask(
    title="LangGraph fundamentals",
    query="What is LangGraph and how does it work?",
)
```

#### `ResearchPlan`

```python
class ResearchPlan(BaseModel):
    tasks: list[ResearchTask]
```

The `Field` configuration requires exactly three tasks:

```python
min_length=3
max_length=3
```

Pydantic validates the LLM response. If the model returns the wrong shape or does not provide three tasks, structured-output validation can reject the response instead of allowing malformed data into the worker stage.

#### `create_plan`

```python
def create_plan(llm: ChatGroq, topic: str) -> ResearchPlan:
```

This function:

1. Receives the configured LLM and user topic.
2. Calls `llm.with_structured_output(ResearchPlan)`.
3. Asks for three independent tasks covering fundamentals, applications, and limitations.
4. Returns a validated `ResearchPlan` object.

The caller can then use:

```python
plan.tasks[0].title
plan.tasks[0].query
```

### `agent.py`

This file defines the work performed by one research agent.

#### `run_task`

```python
def run_task(llm: ChatGroq, task_title: str, query: str) -> str:
```

This function:

1. Receives one planned task.
2. Calls `web_search` with the task query.
3. Sends the task title, query, and search results to the LLM.
4. Asks the LLM to extract relevant facts and separate evidence from unsupported claims.
5. Returns the worker's analysis as a string.

The worker does not create the overall plan and does not synthesize the final report. It has one focused responsibility.

### `main.py`

This file coordinates the entire application.

#### `synthesize_report`

```python
def synthesize_report(llm: ChatGroq, topic: str, results: list[str]) -> str:
```

This function receives the three worker outputs. It builds one prompt containing all results and asks the LLM to:

- combine the findings
- compare agreements and disagreements
- identify limitations
- produce practical conclusions

It returns the final report text.

#### `research`

```python
def research(topic: str) -> str:
```

This is the main application workflow:

1. Creates one `ChatGroq` instance.
2. Calls `create_plan` to produce three tasks.
3. Creates a `ThreadPoolExecutor` with three workers.
4. Calls `run_task` once for each planned task.
5. Waits for all worker results.
6. Calls `synthesize_report`.
7. Writes the report using UTF-8 encoding.
8. Returns and prints the report.

The parallel section is:

```python
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(run_task, llm, task.title, task.query)
        for task in plan.tasks
    ]
    results = [future.result() for future in futures]
```

`executor.submit` starts each task independently. `future.result()` waits for each task to finish and returns its result.

#### Script entry point

```python
if __name__ == "__main__":
```

This ensures the interactive program runs only when `main.py` is executed directly. It asks for the topic, rejects an empty topic, and calls `research(topic)`.

## Complete Example

For this input:

```text
Compare LangGraph and CrewAI for building multi-agent systems.
```

The planner may return a structure like:

```python
ResearchPlan(
    tasks=[
        ResearchTask(
            title="Fundamentals",
            query="LangGraph and CrewAI architecture and core concepts",
        ),
        ResearchTask(
            title="Practical applications",
            query="LangGraph and CrewAI production use cases",
        ),
        ResearchTask(
            title="Limitations and tradeoffs",
            query="LangGraph vs CrewAI limitations cost scalability and complexity",
        ),
    ]
)
```

The three workers then run independently:

```text
Worker 1 -> web_search("LangGraph and CrewAI architecture and core concepts")
Worker 2 -> web_search("LangGraph and CrewAI production use cases")
Worker 3 -> web_search("LangGraph vs CrewAI limitations cost scalability and complexity")
```

Each worker sends its search results to the LLM and returns an analysis. The synthesizer receives the three analyses:

```text
Task 1 result: architecture and fundamentals
Task 2 result: practical applications
Task 3 result: limitations and tradeoffs
```

It then produces a report such as:

```markdown
# LangGraph vs CrewAI

## Architecture
...

## Practical Applications
...

## Limitations and Tradeoffs
...

## Conclusion
...
```

That report is saved to:

```text
02_single_agents/research_agent/research_agent_1/research_report.md
```

## Why Use Three Agents?

Splitting the research into independent tasks has several benefits:

- Each worker has a narrower prompt.
- Different aspects of the topic can be researched separately.
- Independent searches can run concurrently.
- The synthesizer can compare findings from multiple perspectives.
- Adding another research dimension only requires changing the plan contract and worker scheduling logic.

The work is parallel, but synthesis remains a separate final step because the final LLM needs all worker results before it can compare them.

## Pydantic's Role

Pydantic is used only for the planner's output contract. It turns the LLM response into predictable Python objects:

```text
Unstructured LLM response
        |
        v
ResearchPlan validation
        |
        v
Three ResearchTask objects
        |
        v
Worker agents
```

Without structured validation, the model might return prose, missing fields, or the wrong number of tasks. With Pydantic, the rest of the program can safely use `task.title` and `task.query`.

## Error and Limitation Notes

- Web search requires network access.
- Groq requests require a valid `GROQ_API_KEY`.
- The program makes multiple LLM calls: one planning call, one call per worker, and one synthesis call.
- Three parallel workers can increase concurrent API usage.
- Search results are external data and may be incomplete or inaccurate; the synthesizer is prompted to identify limitations, but its report should still be reviewed.
- A failed worker currently causes the corresponding future to raise an exception. Production code should add retries and per-task error handling.
- `max_workers=3` matches the planner's requirement of exactly three tasks. If the plan size changes, update the executor configuration as appropriate.

## Validation

Compile the files without making network or LLM requests:

```powershell
python -m py_compile `
  .\02_single_agents\research_agent\research_agent_1\tools.py `
  .\02_single_agents\research_agent\research_agent_1\planner.py `
  .\02_single_agents\research_agent\research_agent_1\agent.py `
  .\02_single_agents\research_agent\research_agent_1\main.py
```

A successful command produces no output.
