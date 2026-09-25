import subprocess
import time
import psutil
import pyautogui

TOOL = {
    "name": "control_hardware",
    "description": (
        "Controls hardware settings or checks device power on Windows: "
        "Checks laptop battery percentage and charging status, "
        "turns WiFi on or off, and toggles Bluetooth on or off."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "The task to perform: 'battery_status', 'wifi_on', 'wifi_off', 'bluetooth_toggle', 'bluetooth_on', 'bluetooth_off'"
            }
        },
        "required": ["action"]
    }
}

def _toggle_bluetooth_settings():
    """Windows Settings এর মাধ্যমে ব্লুটুথ টগল করার নির্ভরযোগ্য পদ্ধতি।"""
    try:
        # Windows Settings এর Bluetooth পেজ ওপেন করা
        subprocess.run(["cmd", "/c", "start", "ms-settings:bluetooth"], shell=True)
        time.sleep(1.2)
        # Tab চেপে টগল সুইচে যাওয়া এবং Space চেপে অন/অফ করা
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('space')
        time.sleep(0.5)
        # সেটিংস উইন্ডো বন্ধ করে দেওয়া
        pyautogui.hotkey('alt', 'f4')
    except Exception as e:
        print(f"[Bluetooth Error]: {e}")

def run(args: dict, context: dict = None) -> str:
    action = str(args.get("action", "")).lower().strip()

    # ১. ব্যাটারি স্ট্যাটাস চেক
    if "battery" in action:
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "ল্যাপটপে কোনো ব্যাটারি পাওয়া যায়নি, এটি সরাসরি চার্জারে চলছে।"
            percent = battery.percent
            plugged = "চার্জ হচ্ছে" if battery.power_plugged else "চার্জারে লাগানো নেই"
            return f"ল্যাপটপের ব্যাটারি চার্জ বর্তমানে {percent}% এবং {plugged}।"
        except Exception as e:
            return f"ব্যাটারি তথ্য পড়তে সমস্যা হয়েছে: {e}"

    # ২. ওয়াইফাই অন বা অফ
    elif action == "wifi_on":
        try:
            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enabled"], capture_output=True, shell=True)
            return "ওয়াইফাই অন করা হয়েছে, বস।"
        except Exception as e:
            return f"ওয়াইফাই চালু করতে সমস্যা হয়েছে: {e}"

    elif action == "wifi_off":
        try:
            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disabled"], capture_output=True, shell=True)
            return "ওয়াইফাই বন্ধ করা হয়েছে, বস।"
        except Exception as e:
            return f"ওয়াইফাই বন্ধ করতে সমস্যা হয়েছে: {e}"

    # ৩. ব্লুটুথ অন বা অফ
    elif "bluetooth" in action:
        try:
            import threading
            threading.Thread(target=_toggle_bluetooth_settings, daemon=True).start()
            return "ব্লুটুথের অবস্থা পরিবর্তন করা হয়েছে, বস।"
        except Exception as e:
            return f"ব্লুটুথ নিয়ন্ত্রণে সমস্যা হয়েছে: {e}"

    return "কমান্ডটি সঠিকভাবে কার্যকর করা সম্ভব হয়নি।"