# Research Agent 0

This project demonstrates a single LLM agent that performs research by calling tools.

The user enters a research topic. The LLM decides which tools to call, receives the tool results, and continues until it can produce a final answer. The agent can search the web, search for research papers, and save a generated report.

## Architecture

```text
USER
  |
  v
agent.py
  |
  v
ChatGroq with bound tools
  |
  +----------------+
  |                |
  v                v
web_search     paper_search
  |                |
  +--------+-------+
           |
           v
      LLM analyzes results
           |
           v
       save_report
           |
           v
  research_report.md
```

Unlike a planner-worker system, this version has one agent and one conversation loop. The LLM itself decides when to search, which search to use, whether to search again, and when to save the report.

## Files

```text
research_agent_0/
|
|-- README.md            This documentation
|-- agent.py             Single-agent tool-calling loop
|-- tool.py              Search, webpage, and report tools
|-- research_report.md   Generated report after a successful run
```

`research_report.md` is runtime output. It is created or overwritten when the `save_report` tool runs.

## Requirements

The code uses:

- Python 3.10 or newer
- `langchain-core`
- `langchain-community`
- `langchain-groq`
- `python-dotenv`
- DuckDuckGo search support through `DuckDuckGoSearchRun`

A Groq API key is required. Put it in a `.env` file loaded by the project:

```env
GROQ_API_KEY=your_api_key_here
```

Do not commit the `.env` file or place the API key directly in Python code.

## Run the Agent

From the repository root:

```powershell
python .\02_single_agents\research_agent\research_agent_0\agent.py
```

Enter a topic when prompted:

```text
What would you like to research? Compare LangGraph and CrewAI for building multi-agent systems.
```

The program prints the tool call selected by the LLM:

```text
Iteration 1: [{'name': 'web_search', 'args': {'query': 'LangGraph vs CrewAI'}}]
Iteration 2: [{'name': 'paper_search', 'args': {'topic': 'multi-agent systems'}}]
Iteration 3: [{'name': 'save_report', 'args': {'report': '# Comparison...'}}]
Iteration 4: []
# Comparison of LangGraph and CrewAI
...
```

An empty tool-call list means the LLM has finished using tools and has returned its final answer.

## `tool.py`

Location: `tool.py`

This file contains the capabilities available to the agent.

### `search_tool`

```python
search_tool = DuckDuckGoSearchRun()
```

Creates the DuckDuckGo search client used by the search functions.

### `search_engine`

```python
def search_engine(query: str):
    return search_tool.invoke(query)
```

A small helper that sends a query to DuckDuckGo and returns the results.

### `web_search`

```python
@tool
def web_search(query: str):
    """Search the web and return results for a research query."""
    return search_engine(query)
```

This is a LangChain tool. It:

1. Receives a normal web-search query.
2. Calls `search_engine`.
3. Returns the search results to the LLM.

Example direct call:

```python
from tool import web_search

result = web_search.invoke({"query": "What is LangGraph?"})
print(result)
```

### `paper_search`

```python
@tool
def paper_search(topic: str):
    query = f"{topic} research papers site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov"
    return search_engine(query)
```

This tool converts a topic into a research-paper search query. It limits the search toward sources such as arXiv and PubMed.

Example:

```python
paper_search.invoke({"topic": "multi-agent systems"})
```

The actual search query becomes similar to:

```text
multi-agent systems research papers site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov
```

### `fetch_webpage`

```python
def fetch_webpage(url: str):
```

This helper downloads a webpage with `urllib.request.urlopen` and decodes its content as UTF-8 when possible.

It uses a 15-second timeout:

```python
with urlopen(url, timeout=15) as response:
```

### `read_url`

```python
@tool
def read_url(url: str):
```

This LangChain tool calls `fetch_webpage` and returns webpage text.

Important: `read_url` is defined in `tool.py`, but the current `agent.py` does not include it in the `tools` list. Therefore, the LLM cannot select it during the normal agent run yet. To make it available, add it to the import and list in `agent.py`:

```python
from tool import paper_search, read_url, save_report, web_search


tools = [web_search, paper_search, read_url, save_report]
```

### `save_report`

```python
@tool
def save_report(report: str):
```

This tool saves the final report:

```python
with open("research_report.md", "w", encoding="utf-8") as f:
    f.write(report)
```

UTF-8 encoding is used so generated reports can contain characters such as em dashes, non-breaking hyphens, and accented letters on Windows.

The tool returns:

```text
Report saved successfully.
```

## `agent.py`

Location: `agent.py`

This file creates the LLM and runs the tool-calling loop.

### Imports and local module path

```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
```

This adds the current folder to Python's import path so `from tool import ...` works when the file is run using its full path.

### Create the model

```python
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)
```

This creates the Groq chat model. A temperature of `0` encourages more deterministic tool selection and report generation.

### Register tools

```python
tools = [web_search, paper_search, save_report]
llm_with_tools = llm.bind_tools(tools)
```

`bind_tools` tells the model which tools it can request. The model does not execute the tools directly. It returns a tool call, and the Python loop executes that call.

The currently registered tools are:

- `web_search`
- `paper_search`
- `save_report`

`read_url` is available in `tool.py` but is not registered by default.

### Create the user message

```python
messages = [
    HumanMessage(
        content=(
            f"Research this topic: {topic}. Use both web_search and paper_search. "
            "Analyze and compare the results, synthesize a concise final report, "
            "then use save_report to save it before giving your final answer."
        )
    )
]
```

The message gives the LLM the topic and instructions. The list is important because it stores the conversation history.

As the loop runs, the list contains:

```text
HumanMessage       User instructions
AIMessage          Model response and tool calls
ToolMessage        Results returned by Python tools
AIMessage          Next model response
```

### Limit iterations

```python
max_iterations = 8
```

This prevents the model from calling tools forever. The agent can make at most eight LLM cycles.

An iteration means:

1. Call the LLM.
2. Inspect its tool calls.
3. Execute requested tools.
4. Add tool results to `messages`.

It does not mean one individual tool call. One LLM response could request multiple tools within one iteration.

### Call the model

```python
response = llm_with_tools.invoke(messages)
messages.append(response)
```

The model reads the conversation history and returns either:

- a final text response, or
- one or more tool calls

The response is appended so the next LLM call can see what happened.

### Detect the final answer

```python
if not response.tool_calls:
    print(response.content)
    break
```

When `response.tool_calls` is empty, the model does not need another tool. Its content is treated as the final answer and the loop stops.

### Select and execute a tool

```python
selected_tool = next(
    tool for tool in tools if tool.name == tool_call["name"]
)
result = selected_tool.invoke(tool_call["args"])
```

The model returns a tool name and arguments. Python finds the matching registered tool and invokes it with those arguments.

For example, the model may return:

```python
{
    "name": "web_search",
    "args": {"query": "LangGraph vs CrewAI"}
}
```

Python then runs:

```python
web_search.invoke({"query": "LangGraph vs CrewAI"})
```

### Return the tool result to the model

```python
messages.append(
    ToolMessage(
        content=str(result),
        tool_call_id=tool_call["id"],
    )
)
```

The tool result is added to the conversation as a `ToolMessage`. The `tool_call_id` connects the result to the original model request.

The next LLM call can now read the search results and decide what to do next.

## Complete Example Flow

For the topic:

```text
Compare LangGraph and CrewAI for building multi-agent systems.
```

The model might produce this sequence:

```text
Iteration 1: web_search
```

Python executes `web_search` and returns web results.

```text
Iteration 2: paper_search
```

Python executes `paper_search` and returns paper-focused results.

```text
Iteration 3: web_search
```

The model may perform another search to investigate memory, scalability, or cost.

```text
Iteration 4: save_report
```

The model sends the generated report to `save_report`.

```text
Iteration 5: []
```

The empty list means the model has finished using tools and returns the final answer.

The complete data flow is:

```text
User topic
    |
    v
HumanMessage
    |
    v
ChatGroq decides next action
    |
    +--> web_search ------+
    |                      |
    +--> paper_search ----+--> ToolMessage with results
    |                      |
    +--> save_report -----+
    |
    v
Final AI response
```

## Single Agent vs Planner-Worker Agent

This version has one agent making all decisions:

```text
One LLM
  |
  +--> web search
  +--> paper search
  +--> save report
```

The related `research_agent_1` version uses a different design:

```text
Planner
  |
  +--> Worker 1
  +--> Worker 2
  +--> Worker 3
  |
  v
Synthesizer
```

`research_agent_0` is simpler and more flexible for small workflows. `research_agent_1` is more structured and can run independent research tasks in parallel.

## Limitations

- The LLM can choose an inefficient sequence of searches.
- The agent can make several API calls before finishing.
- `max_iterations` limits loops but does not enforce a token or money budget.
- Search results may be incomplete or inaccurate.
- `read_url` is not currently registered in `agent.py`.
- Tool lookup assumes the model returns a valid registered tool name.
- A failed search or save operation currently raises an exception and stops the run.

## Validation

Compile the files without making LLM or network requests:

```powershell
python -m py_compile `
  .\02_single_agents\research_agent\research_agent_0\tool.py `
  .\02_single_agents\research_agent\research_agent_0\agent.py
```

A successful command produces no output.
