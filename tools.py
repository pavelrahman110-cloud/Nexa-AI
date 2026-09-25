import time
import webbrowser
import urllib.parse
import pyautogui
import pyperclip
import threading

def _pause_and_search_worker(song_name: str):
    """চলমান গান পজ করে একই ট্যাবে নতুন গান সার্চ করে।"""
    try:
        # ১. স্পেস চেপে বা 'k' চেপে ইউটিউব ভিডিও পজ করা
        pyautogui.press('k')
        time.sleep(0.3)

        # ২. ইউটিউবের সার্চ বারে যাওয়া ('/' শর্টকাট)
        pyautogui.press('/')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

        # ৩. নতুন গান লিখে সার্চ দেওয়া
        pyperclip.copy(song_name)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(1.5)

        # ৪. প্রথম গানটি প্লে করার জন্য এন্টার
        pyautogui.press('enter')
    except Exception as e:
        print(f"[Media Action Error]: {e}")

def pause_and_change_song(song_name: str) -> str:
    """বর্তমান গান পজ করে একই ট্যাবে নতুন গান সার্চ ও প্লে করে।"""
    threading.Thread(target=_pause_and_search_worker, args=(song_name,), daemon=True).start()
    return f"বর্তমান গানটি পজ করে {song_name} সার্চ করা হচ্ছে, বস।"

def pause_current_media() -> str:
    """চলমান গান বা ভিডিও পজ অথবা রিজিউম করে।"""
    try:
        pyautogui.press('space')
        return "ভিডিও পজ করা হয়েছে, বস।"
    except Exception as e:
        return f"সমস্যা হয়েছে: {e}"