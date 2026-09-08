from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


search_tool = DuckDuckGoSearchRun()


def search_engine(query: str):
    return search_tool.invoke(query)


@tool
def web_search(query: str):
    """Search the web and return results for a research query."""
    return search_engine(query)


@tool
def paper_search(topic: str):
    """Search for research papers related to a topic."""
    query = f"{topic} research papers site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov"
    return search_engine(query)


def fetch_webpage(url: str):
    """Fetch the text content of a webpage."""
    from urllib.request import urlopen

    with urlopen(url, timeout=15) as response:
        return response.read().decode("utf-8", errors="ignore")

@tool
def read_url(url: str):
    """Read the text content from a webpage URL."""
    content = fetch_webpage(url)
    return content


@tool
def save_report(report: str):
    """Save the research report to research_report.md."""
    with open("research_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    return "Report saved successfully."