import os
import subprocess
import platform

TOOL = {
    "name": "open_app",
    "description": "Opens a desktop application or software by its name (e.g., chrome, notepad, spotify, vlc).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app_name": {
                "type": "STRING",
                "description": "The name of the application to open."
            }
        },
        "required": ["app_name"]
    }
}

def open_application(app_name: str) -> str:
    """Safely opens an application across Windows, macOS, and Linux."""
    app_name = app_name.lower().strip()
    system = platform.system()
    
    try:
        if system == "Windows":
            # Common application path shortcuts or direct execution
            if "chrome" in app_name:
                os.system("start chrome")
            elif "notepad" in app_name:
                os.system("start notepad")
            elif "calculator" in app_name or "calc" in app_name:
                os.system("calc")
            else:
                os.system(f"start {app_name}")
        elif system == "Darwin": # macOS
            subprocess.Popen(["open", "-a", app_name])
        else: # Linux
            subprocess.Popen([app_name])
            
        return f"Successfully opened {app_name}."
    except Exception as e:
        return f"Failed to open {app_name}. Error: {str(e)}"

def run(args, context=None):
    app_name = args.get("app_name", "")
    if not app_name:
        return "Please specify the application name."
    return open_application(app_name)