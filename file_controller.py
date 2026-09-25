import os
import shutil

TOOL = {
    "name": "file_controller",
    "description": "Performs file operations such as creating, deleting, moving, or reading files.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Action to perform: 'read', 'delete', or 'create'."
            },
            "path": {
                "type": "STRING",
                "description": "The file or directory path."
            },
            "content": {
                "type": "STRING",
                "description": "Content for creating or writing files (optional)."
            }
        },
        "required": ["action", "path"]
    }
}

def control_file(action: str, path: str, content: str = "") -> str:
    action = action.lower().strip()
    try:
        if action == "read":
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            return f"File not found: {path}"
            
        elif action == "create":
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully created/written to file: {path}"
            
        elif action == "delete":
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                return f"Successfully deleted: {path}"
            return f"Path not found: {path}"
            
        else:
            return f"Unknown file action: {action}"
    except Exception as e:
        return f"File operation failed. Error: {str(e)}"

def run(args, context=None):
    return control_file(args.get("action", ""), args.get("path", ""), args.get("content", ""))