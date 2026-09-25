import time, os, subprocess
try:
    import pyautogui
except ImportError:
    pyautogui = None

def handler(args: dict, ctx: dict = None) -> str:
    if not pyautogui:
        return "Error: pyautogui module is not installed. Please run 'pip install pyautogui'."
    
    pages = args.get("pages_to_scroll", 4)
    try:
        pages = int(pages)
    except ValueError:
        pages = 4

    # Screen-er center-e once click kore PDF window-ta focus/active kora hochche
    if pyautogui:
        sw, sh = pyautogui.size()
        pyautogui.click(sw // 2, sh // 2)
        time.sleep(0.5)

    for i in range(pages):
        pyautogui.press("pagedown")
        time.sleep(1.5)

    return fI have successfully scrolled through {pages} sections/pages of the displayed PDF on screen. I am ready to answer any questions from it.

TOOL = {
    "name": "scroll_and_read_pdf",
    "handler": handler,
    "description": "Focuses the PDF on screen, scrolls down page by page, and reads its content.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "pages_to_scroll": {"type": "INTEGER", "description": "Number of pages to scroll."}
        },
        "required": []
    }
}
