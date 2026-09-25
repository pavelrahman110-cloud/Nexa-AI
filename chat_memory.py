import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path(__file__).resolve().parent.parent / "core" / "recent_chat_history.json"
MAX_SAVED_TURNS = 12  # শেষ কতগুলো প্রশ্নোত্তর হুবহু মনে রাখবে

def append_to_history(role: str, text: str):
    """ব্যবহারকারী এবং নেক্সার পুরো কথোপকথন ফাইলে জমিয়ে রাখে।"""
    if not text or not text.strip():
        return

    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append({
        "role": role,
        "text": text.strip(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    # ফাইলের সাইজ ঠিক রাখতে শেষ ১২টি টার্ন সংরক্ষণ করে
    history = history[-MAX_SAVED_TURNS:]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ChatMemory] Save error: {e}")

def get_recent_history_context() -> str:
    """নতুন সেশনে অতীতের পুরো কথোপকথন ফিরিয়ে দেয়।"""
    if not HISTORY_FILE.exists():
        return ""

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

        if not history:
            return ""

        context_lines = ["[PREVIOUS DETAILED CONVERSATION CONTEXT]"]
        for turn in history:
            speaker = "Boss" if turn["role"] == "user" else "Nexa"
            context_lines.append(f"{speaker}: {turn['text']}")

        return "\n".join(context_lines)
    except Exception as e:
        print(f"[ChatMemory] Read error: {e}")
        return ""