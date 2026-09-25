import os, subprocess, string
from pathlib import Path

skip_dirs = {"System Volume Information", "$RECYCLE.BIN", "Windows", "AppData", "_pycache_", ".files"}

def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        dp = f_{letter}:\\\
        if os.path.exists(dp):
            drives.append(dp)
    return drives if drives else ["C:\\\", "D:\\\"]

def search_paths(term: str, max_r: int = 5):
    term = term.lower().strip()
    found = []
    drives = get_available_drives()
    for dr in drives:
        try:
            for root, dirs, files in os.walk(dr):
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
                for item in dirs + files:
                    if term in item.lower():
                        full_p = os.path.join(root, item)
                        found.append(full_p)
                        if len(found) >= max_r:
                            return found
        except Exception:
            continue
    return found

def handler(args: dict, ctx: dict = None) -> str:
    name = str(args.get("folder_name", "") or args.get("query", "")).strip()
    if not name:
        return "Error: No folder or file name provided."
    results = search_paths(name)
    if not results:
        return fNothing found for '{name}' across C: or D: drives."
    first = results[0]
    try:
        if os.path.isdir(first):
            os.startfile(first)
        else:
            subprocess.Popen(f"explorer /select,\"{first}\"")
    except Exception as e:
        pass
    return f"Found at: {first} (Opened on screen)"

TOOL = {
    "name": "folder_finder",
    "handler": handler,
    "description": "Search for any folder or file across all drives and open it.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "folder_name": {"type": "STRING", "description": "Name of folder or file to find."}
        },
        "required": ["folder_name"]
    }
}
