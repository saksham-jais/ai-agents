from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from tools import web_search


def run_task(llm: ChatGroq, task_title: str, query: str) -> str:
	search_results = web_search.invoke({"query": query})
	response = llm.invoke(
		[
			HumanMessage(
				content=(
					f"Research task: {task_title}\n"
					f"Search query: {query}\n\n"
					f"Search results:\n{search_results}\n\n"
					"Extract the most relevant facts for the final report. "
					"Separate evidence from unsupported claims."
				)
			)
		]
	)
	return response.content
