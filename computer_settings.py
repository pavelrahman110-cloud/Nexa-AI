import os, re
try:
    from ctypes import cast, POINTER
    from comtypes import CLS_ALL, CLSTX_CONTEXT_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    has_pycaw = True
except ImportError:
    has_pycaw = False

import pyautogui

def set_exact_volume(pct: int) -> bool:
    if not has_pycaw: return False
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 23, 1, None)
        vol = cast(interface, POINTER(IAudioEndpointVolume))
        scalar = max(0.0, min(1.0, pct / 100.0))
        vol.SetMasterVolumeLevelScalar(scalar, None)
        return True
    except Exception:
        pass
    return False

def handler(args: dict, ctx: dict = None) -> str:
    act = str(args.get("action", "")).lower()
    val_raw = str(args.get("value", ""))
    match = re.search(r'\d', val_raw or act)
    
    if match:
        pct = int(match.group(0))
        if set_exact_volume(pct):
            return fVolume successfully set to {pct}%."
    
    if "up" in act or "increase" in act:
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Volume turned up."
    elif "down" in act or "decrease" in act or "comao" in act:
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Volume turned down."
    elif "mute" in act:
        pyautogui.press("volumemute")
        return "Volume muted successfully."
    
    return "Settings updated."


TOOL = {
    "name": "computer_settings",
    "handler": handler,
    "description": "Adjust system volume up, down, mute, or set an exact percentage.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "action name (such as volume_set, volume_up, volume_down, mute)"},
            "value": {"type": "INTEGER", "description": "exact percentage number (such as 38, 50, 70)"}
        },
        "required": ["action"]
    }
}
