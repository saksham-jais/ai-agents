def search_web(query: str, limit: int = 5) -> str:
    try:
        from ddgs import DDGS

        results = DDGS().text(query, max_results=limit)
        return "\n".join(
            f"- {item.get('title', '')}: {item.get('body', '')} ({item.get('href', '')})"
            for item in results
        ) or "No live search results found."
    except Exception as error:
        return f"Live search unavailable ({type(error).__name__}); verify current details manually."