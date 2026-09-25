import pyautogui
import time

TOOL = {
    "name": "computer_control",
    "description": "Controls computer mouse and keyboard to perform clicks, type text, or press shortcuts.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "The action to perform: 'type', 'press', 'click', or 'move'."
            },
            "value": {
                "type": "STRING",
                "description": "The text to type, key to press, or coordinates for click (e.g. '100,200')."
            }
        },
        "required": ["action"]
    }
}

def control_computer(action: str, value: str = "") -> str:
    """Executes mouse or keyboard actions safely."""
    action = action.lower().strip()
    try:
        if action == "type":
            if not value:
                return "No text provided to type."
            time.sleep(0.5)
            pyautogui.write(value, interval=0.05)
            return f"Typed: '{value}'"
            
        elif action == "press":
            if not value:
                return "No key provided to press."
            pyautogui.press(value.lower())
            return f"Pressed key: {value}"
            
        elif action == "click":
            if value and "," in value:
                x, y = map(int, value.split(","))
                pyautogui.click(x, y)
                return f"Clicked at coordinates ({x}, {y})"
            else:
                pyautogui.click()
                return "Clicked current mouse position."
                
        else:
            return f"Unknown computer control action: {action}"
    except Exception as e:
        return f"Computer control failed. Error: {str(e)}"

def run(args, context=None):
    action = args.get("action", "")
    value = args.get("value", "")
    return control_computer(action, value)