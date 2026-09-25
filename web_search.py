import urllib.parse
import webbrowser

TOOL = {
    "name": "web_search",
    "description": "Performs a web search to find live information, news, or answers online.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search topic or question."
            }
        },
        "required": ["query"]
    }
}

def search_web(query: str) -> str:
    query = query.strip()
    if not query:
        return "Search query cannot be empty."
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://duckduckgo.com/?q={encoded}"
        webbrowser.open(url, new=2)
        return f"Opened web search for: '{query}'"
    except Exception as e:
        return f"Web search failed. Error: {str(e)}"

def _news(query: str = "latest news") -> str:
    """Fetches news (compatible helper for main.py)."""
    return search_web(query)

def run(args, context=None):
    return search_web(args.get("query", ""))