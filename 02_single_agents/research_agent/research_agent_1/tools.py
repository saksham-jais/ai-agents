from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool


search_engine = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
	"""Search the web and return relevant results for a research task."""
	return search_engine.invoke(query)
