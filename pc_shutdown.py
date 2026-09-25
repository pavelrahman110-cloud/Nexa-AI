"""
actions/pc_shutdown.py — Windows Direct Shutdown Tool
"""
import subprocess

TOOL = {
    "name": "system_shutdown",
    "description": (
        "Completely powers off the laptop immediately without any confirmation. "
        "Call this whenever Pavel says 'ল্যাপটপ বন্ধ করো' or 'shutdown laptop'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    },
    "require_confirmation": False,
    "safe": True
}

def run(args: dict, ctx: dict) -> str:
    try:
        # কোনো কনফার্মেশন ছাড়া সরাসরি ৩ সেকেন্ডে শাটডাউন
        subprocess.Popen(["shutdown", "/s", "/f", "/t", "3"], shell=True)
        return "ল্যাপটপ শাটডাউন করা হচ্ছে, পাভেল স্যার!"
    except Exception as e:
        return f"শাটডাউন করতে সমস্যা হয়েছে: {e}"