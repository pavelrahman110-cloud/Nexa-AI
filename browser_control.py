import webbrowser

TOOL = {
    "name": "browser_control",
    "description": "Opens the default web browser and searches or navigates to a given URL or query.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query or website URL to open."
            }
        },
        "required": ["query"]
    }
}

def control_browser(query: str) -> str:
    """Opens a URL or performs a Google search if it's a query."""
    query = query.strip()
    if not query:
        return "Query cannot be empty."
    
    try:
        if query.startswith("http://") or query.startswith("https://"):
            webbrowser.open(query)
            return f"Opened URL: {query}"
        elif "." in query and " " not in query:
            url = f"https://{query}"
            webbrowser.open(url)
            return f"Opened website: {url}"
        else:
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            return f"Searched for '{query}' on the browser."
    except Exception as e:
        return f"Browser control failed. Error: {str(e)}"

def run(args, context=None):
    query = args.get("query", "")
    return control_browser(query)