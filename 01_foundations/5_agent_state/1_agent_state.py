import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "2_tools" / "1_Custom_Tools"),
)

from langchain_groq import ChatGroq
from custom_tool_1 import TOOL_REGISTRY, get_tool
from langchain_core.messages import HumanMessage, ToolMessage
from dotenv import load_dotenv

load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

llm_with_tools = llm.bind_tools(
    list(TOOL_REGISTRY.values())
)


class AgentState(TypedDict):
    messages: list
    iteration: int
    max_iterations: int
    final_answer: str


question = "Calculate 500 / 25, then multiply by 10."
state: AgentState = {
    "messages": [HumanMessage(content=question)],
    "iteration": 0,
    "max_iterations": 5,
    "final_answer": "",
}

while state["iteration"] < state["max_iterations"]:
    state["iteration"] += 1
    response = llm_with_tools.invoke(state["messages"])
    state["messages"].append(response)

    print(f"Iteration {state['iteration']}: {response.tool_calls}")

    # No tool calls means the model has produced its final answer.
    if not response.tool_calls:
        state["final_answer"] = response.content
        print(state["final_answer"])
        break

    for tool_call in response.tool_calls:
        tool = get_tool(tool_call["name"])

        try:
            result = tool.invoke(tool_call["args"])
        except Exception as error:
            result = f"Tool error: {error}"

        state["messages"].append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )

if not state["final_answer"]:
    print(
        f"Agent stopped after {state['max_iterations']} iterations "
        "without a final answer."
    )

print(state["messages"])