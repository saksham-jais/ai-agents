# AI Agents Learning Repository

A progressive collection of Python examples for building LLM applications and
agent systems with LangChain, LangGraph, Groq, Pydantic, ChromaDB, and common
Python concurrency tools.

The repository is organized as a learning path. Start with `01_foundations`,
then move through single agents, memory and retrieval, multi-agent workflows,
and advanced patterns. The folders are intentionally separate examples rather
than one installable package, so most scripts should be run from the repository
root using their file path.

## What You Will Learn

```text
01_foundations       Model calls, tools, tool calling, structured output, state
02_single_agents     Complete agents for research, support, coding, and search
03_memory_and_rag    Conversation memory, semantic memory, vectors, and RAG
04_multi_agent       Supervisor teams, parallel review, and specialist agents
05_advanced_agents   MCP, planning, reflection, autonomy, and self-correction
06_real_world_projects Larger application blueprints
experiments          Ideas, prompts, and model comparisons
```

## Quick Start

### 1. Create an environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\python312-requirements.txt
```

Use `python314-requirements.txt` when running Python 3.14. The requirements
files are environment snapshots and contain more packages than every individual
example needs.

### 2. Configure API keys

Copy `.env.example` to `.env` and add your credentials:

```powershell
Copy-Item .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key
HUGGINGFACEHUB_ACCESS_TOKEN=your_huggingface_token
```

Most examples use Groq through `ChatGroq`. The Hugging Face token is needed by
some embedding examples. Never commit `.env` or put keys in source code.

### 3. Run an example

From the repository root:

```powershell
python .\01_foundations\1_basic_agent\agent.py
python .\04_multi_agent\multi-agent-parallel\main.py
```

Some modules use local imports. Running the script by its path, as shown above,
keeps those imports working for the current examples.

## How the Repository Works

Most examples follow this pipeline:

```text
User input
	 |
	 v
ChatGroq model <---- prompt or structured schema
	 |
	 +---- optional tools: search, calculator, weather, shell, web pages
	 |
	 +---- optional memory: JSON, embeddings, or ChromaDB
	 |
	 v
Answer, report, artifact, or agent state
```

`ChatGroq` sends prompts to the Groq API. LangChain tools expose Python
functions to the model. Pydantic models validate structured model responses.
Async examples use `asyncio` to overlap independent network calls. Embeddings
turn text into vectors so semantically related memories can be retrieved even
when the wording is different.

## 01 Foundations

These examples introduce the pieces used by the later projects.

### `01_foundations/1_basic_agent`

- `agent.py`: smallest agent example using `ChatGroq` and a DuckDuckGo search
	tool.
- `README.md`: local notes for this example.

The model receives a user question and can use search when it needs current
information. This is the first example to study for the basic model-plus-tool
relationship.

### `01_foundations/2_tools`

Demonstrates several ways to expose capabilities to an LLM:

- `1_Custom_Tools/custom_tool_0.py`: a minimal typed multiplication tool.
- `1_Custom_Tools/custom_tool_1.py`: calculator, time, and weather tools with a
	tool registry and ordinary Python implementations.
- `2_Structured_Tools/structuredtool.py`: creates a `StructuredTool` backed by
	a Pydantic input schema.
- `search_tools/DuckDuckGodSearchTool.py`: wraps DuckDuckGo search.
- `shelltools/shelltool.py`: invokes LangChain's shell tool. Treat this as a
	demonstration only; arbitrary shell execution must be restricted in real
	applications.

### `01_foundations/3_tool_calling`

- `1_tool_calling.py`: binds tools to `ChatGroq`, sends a question, and handles
	a model-generated tool call.
- `2_Agent_Loop.py`: repeats the model/tool exchange until the model returns a
	final answer.
- `README.md`: detailed explanation of the tool-calling flow.

The important distinction is that the model does not directly execute Python.
It requests a named tool with arguments; the application executes the tool and
returns a `ToolMessage` to the model.

### `01_foundations/4_structured_output`

- `agent.py`: asks the model for data matching a Pydantic schema.
- `README.md`: explanation of validated structured output.

This is useful when application code needs fields and types instead of free
form prose.

### `01_foundations/5_agent_state`

- `1_agent_state.py`: stores messages and tool results in an explicit typed
	state while an agent loop runs.

State is the bridge from a one-shot prompt to a repeatable workflow.

## 02 Single Agents

These folders combine a model, prompts, tools, and application logic into
purpose-specific agents.

### `02_single_agents/research_agent`

#### `research_agent_0`

- `agent.py`: tool-calling research agent.
- `tool.py`: web search, paper search, webpage fetching, and report saving.
- `research_report.md`: generated or example report output.
- `README.md`: local documentation.

This version lets one agent decide which research tools to use.

#### `research_agent_1`

- `main.py`: coordinates planning, parallel workers, synthesis, and report
	saving.
- `planner.py`: creates a validated three-task `ResearchPlan`.
- `agent.py`: performs one focused worker task.
- `tools.py`: DuckDuckGo-backed search tool.
- `research_report.md`: generated final report.
- `README.md`: detailed architecture and run instructions.

The workflow is planner -> three independent workers -> synthesizer. The worker
calls are run concurrently with `ThreadPoolExecutor`, then their results are
combined into one Markdown report.

### Other single-agent application folders

- `coding_agent`: intended home for a coding-focused agent.
- `customer_support_agent`: intended home for a support agent.
- `data_analysis_agent`: intended home for a data-analysis agent.
- `web_search_agent`: intended home for a search-focused agent.

These folders are currently placeholders in the repository inventory and do not
contain runnable source files yet.

## 03 Memory and RAG

### `03_memory_and_rag/conversation_memory`

- `agent_1.py`: decides whether a user message contains a durable memory and
	generates an answer.
- `memory_1.py`: reads and writes JSON memory.
- `main_1.py`: interactive conversation loop.
- `memory.json`: local persisted conversation memory.

This is explicit memory: the program chooses what to store, saves it as JSON,
retrieves it later, and includes it in the next answer.

### `03_memory_and_rag/semantic-memory-agent--memory-augmented-agent`

- `agent.py`: decides whether to create, update, delete, or retrieve a memory,
	then answers using relevant memories.
- `memory.py`: creates embeddings with
	`BAAI/bge-small-en-v1.5` and stores/searches records in ChromaDB.
- `main.py`: interactive memory-augmented chat loop.
- `memory_db/`: persistent ChromaDB data created by the example.

The flow is message -> memory action -> vector retrieval -> answer. This is
semantic memory: retrieval is based on vector similarity rather than exact
keyword matches.

### `long_term_memory`, `rag_agent`, and `vector_memory`

These are reserved areas for longer-term memory, retrieval-augmented
generation, and vector-memory experiments. They currently contain no runnable
source files in this checkout.

## 04 Multi-Agent Systems

### `04_multi_agent/multi_agent.py`

This single-file supervisor loop has three roles:

1. `coder_agent` generates or revises Python code.
2. `reviewer_agent` returns an approved or changes-requested JSON verdict.
3. `supervisor` routes review feedback back to the coder until approval or the
	 maximum revision count is reached.

It also records handoffs in `TeamState.messages` and retries failed Groq calls.
The embedding model is initialized in this file but is not used by this
workflow.

Run it with:

```powershell
python .\04_multi_agent\multi_agent.py\multi_agent.py
```

### `04_multi_agent/multi-agent-parallel`

- `agents.py`: security, performance, architecture, and synthesis agents.
- `main.py`: sends the same code to the three specialist agents concurrently
	with `asyncio.gather`, then sends all findings to the synthesizer.

This is the fan-out/fan-in pattern:

```text
Code -> security       -+
		 -> performance      +-> synthesis -> final review
		 -> architecture   -+
```

`async def` defines a task that can pause while waiting for an API response.
`await` yields control to other tasks, and `asyncio.gather` waits for the
independent specialist calls together. This reduces total waiting time compared
with making the three network calls sequentially.

Run it with:

```powershell
python .\04_multi_agent\multi-agent-parallel\main.py
```

### `04_multi_agent/AI-Software-Development-Team`

This is the most complete multi-agent project in the repository:

- `main.py`: accepts a software task and prints the final result.
- `supervisor.py`: routes research, coding, review, and finish states.
- `researcher.py`: performs structured research.
- `coder.py`: generates a `CodeArtifact`.
- `reviewer.py`: evaluates the artifact with a structured `ReviewReport`.
- `models.py`: Pydantic schemas for routing, issues, reviews, artifacts, and
	final results.
- `config.py`: Groq model, embeddings, structured invocation, and retry setup.
- `memory_store.py`: persists team outcomes and searches related previous work.
- `artifacts.py`: writes generated files and runs generated tests.
- `web_search.py`: web-search integration.
- `tests/test_team_primitives.py`: unit tests for core routing and artifact
	behavior.

The supervisor can use previous memory, research a task, create code, review
it, revise it, write the result to a generated project directory, and run its
tests. Its iteration budget is controlled by `MAX_ITERATIONS`.

### Other multi-agent folders

- `debate_agents`: reserved for debate-style agents.
- `planner_executor`: reserved for planner/executor workflows.
- `researcher_writer`: reserved for researcher/writer workflows.
- `supervisor_workers`: reserved for supervisor and worker experiments.

These folders currently contain no runnable source files in this checkout.

## 05 Advanced Agents

- `agent_with_mcp`: reserved for Model Context Protocol integration.
- `autonomous_research`: reserved for autonomous research loops.
- `planning_agent`: reserved for planning-focused agents.
- `reflection_agent`: reserved for reflection and self-critique.
- `self-correcting-coder`: contains the initial `critic.py`, `generator.py`,
	`state.py`, and `tester.py` modules for a coder that generates, tests, and
	corrects code. `main.py` is currently empty, so this is a scaffold rather
	than a complete runnable project.

## 06 Real-World Projects

The following folders are application-level placeholders for combining the
patterns learned earlier:

- `ai_research_assistant`: research assistant application.
- `business_analyst`: business-analysis application.
- `coding_assistant`: coding assistant application.
- `personal_assistant`: personal assistant application.

They currently contain no runnable source files in this checkout.

## Experiments

- `experiments/ideas`: unfinished ideas and prototypes.
- `experiments/model_comparisons`: comparisons between model providers or
	configurations.
- `experiments/prompts`: prompt drafts and prompt experiments.

Experiments are intentionally less stable than the numbered learning path.

## Running Tests

The software-development-team project has unit tests. Run them from its folder
so its local imports resolve:

```powershell
Push-Location .\04_multi_agent\AI-Software-Development-Team
python -m unittest discover -s tests -p "test_*.py"
Pop-Location
```

For a quick syntax check across the implemented examples:

```powershell
python -m compileall .\01_foundations .\02_single_agents .\03_memory_and_rag .\04_multi_agent .\05_advanced_agents
```

## Important Notes

- Most examples make live model or search requests and require network access.
- Groq rate limits can affect runs; the more complete examples include retry
	handling, but retries do not eliminate provider limits.
- Search and shell tools execute external operations. Restrict inputs and
	permissions before adapting them for production.
- JSON files and `memory_db` contain local state generated by examples. Delete
	them when you want a clean memory demonstration.
- The code is educational and intentionally shows multiple styles. Some later
	directories are scaffolds and should not be treated as finished products.