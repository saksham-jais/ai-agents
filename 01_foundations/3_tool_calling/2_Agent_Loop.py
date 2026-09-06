import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "tools" / "1_Custom_Tools"),
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

question = "Use the weather tool for Indore and use the calculator tool to calculate 10 multiplied by 5."
messages = [HumanMessage(content=question)]
max_iterations = 5

for iteration in range(max_iterations):
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    print(f"Iteration {iteration + 1}: {response.tool_calls}")

    # No tool calls means the model has produced its final answer.
    if not response.tool_calls:
        print(response.content)
        break

    for tool_call in response.tool_calls:
        tool = get_tool(tool_call["name"])

        try:
            result = tool.invoke(tool_call["args"])
        except Exception as error:
            result = f"Tool error: {error}"

        messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )
else:
    print(f"Agent stopped after {max_iterations} iterations without a final answer.")