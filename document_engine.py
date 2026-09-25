import os

TOOL = {
    "name": "document_engine",
    "description": "Reads and extracts text from local text files or documents.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "file_path": {
                "type": "STRING",
                "description": "The path to the document file."
            }
        },
        "required": ["file_path"]
    }
}

def read_document(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Document not found at {file_path}"
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read(2000) # Read first 2000 characters to prevent overflow
        return f"Document content excerpt:\n{text}"
    except Exception as e:
        return f"Failed to read document. Error: {str(e)}"

def run(args, context=None):
    return read_document(args.get("file_path", ""))