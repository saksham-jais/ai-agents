import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_groq import ChatGroq

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tool import paper_search, save_report, web_search


load_dotenv()


llm = ChatGroq(
	model="openai/gpt-oss-20b",
	temperature=0,
)

tools = [web_search, paper_search, save_report]
llm_with_tools = llm.bind_tools(tools)

if __name__ == "__main__":
	topic = input("What would you like to research? ").strip()
	if not topic:
		raise SystemExit("A research topic is required.")

	messages = [
		HumanMessage(
			content=(
				f"Research this topic: {topic}. Use both web_search and paper_search. "
				"Analyze and compare the results, synthesize a concise final report, "
				"then use save_report to save it before giving your final answer."
			)
		)
	]
	max_iterations = 8

	for iteration in range(max_iterations):
		response = llm_with_tools.invoke(messages)
		messages.append(response)
		print(f"Iteration {iteration + 1}: {response.tool_calls}")

		if not response.tool_calls:
			print(response.content)
			break

		for tool_call in response.tool_calls:
			selected_tool = next(
				tool for tool in tools if tool.name == tool_call["name"]
			)
			result = selected_tool.invoke(tool_call["args"])
			messages.append(
				ToolMessage(
					content=str(result),
					tool_call_id=tool_call["id"],
				)
			)
	else:
		print(f"Agent stopped after {max_iterations} iterations.")
