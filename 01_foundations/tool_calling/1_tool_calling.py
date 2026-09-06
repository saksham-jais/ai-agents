import sys
import os
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

question = "What is the weather of Indore?"
response = llm_with_tools.invoke(question)

print(response.tool_calls)

tool_messages = [HumanMessage(content=question), response]

print()

for tool_call in response.tool_calls:
    tool = get_tool(tool_call["name"])
    # print(tool)
    result = tool.invoke(tool_call["args"])
    tool_messages.append(
        ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
        )
    )

print()
print(tool_messages)
print()

final_response = llm_with_tools.invoke(tool_messages)
print(final_response.content)