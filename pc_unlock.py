"""
actions/pc_unlock.py — Direct Hardware ScanCode Unlocker for Windows Lockscreen
"""
import time
import ctypes

USER_KEY = "Pavel110@"

TOOL = {
    "name": "activate_screen_display",
    "description": (
        "Powers on the display monitor, clears the screensaver, and brings Windows back to active state. "
        "Call this whenever Pavel says 'unlock laptop', 'ল্যাপটপ আনলক করো', 'পিসি খোলো', or 'wake up'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    },
}

KEYEVENTF_KEYUP = 0x0002
VK_RETURN = 0x0D
VK_SPACE = 0x20
VK_SHIFT = 0x10

# মাউস ইভেন্ট ফ্ল্যাগ
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

def _press_vk(vk_code):
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.06)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.06)

def _click_center():
    # স্ক্রিনের মাঝামাঝি ক্লিক করে পাসওয়ার্ড বক্সে জোরপূর্বক ফোকাস নেওয়া
    user32 = ctypes.windll.user32
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    user32.SetCursorPos(w // 2, int(h * 0.60))
    time.sleep(0.1)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.1)

def _type_hardware_key(char):
    user32 = ctypes.windll.user32
    # VkKeyScanEx দিয়ে উইন্ডোজের কারেন্ট কীবোর্ড থেকে সঠিক ভার্চুয়াল কি ও শিফট স্টেট বের করা
    res = user32.VkKeyScanW(ord(char))
    vk_code = res & 0xFF
    shift_state = (res >> 8) & 1

    # হার্ডওয়্যার স্ক্যান কোড বের করা (উইন্ডোজ লকস্ক্রিন শুধু স্ক্যান কোড গ্রহণ করে)
    scan_code = user32.MapVirtualKeyW(vk_code, 0)

    if shift_state:
        shift_scan = user32.MapVirtualKeyW(VK_SHIFT, 0)
        user32.keybd_event(VK_SHIFT, shift_scan, 0, 0)
        time.sleep(0.04)

    user32.keybd_event(vk_code, scan_code, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, scan_code, KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)

    if shift_state:
        shift_scan = user32.MapVirtualKeyW(VK_SHIFT, 0)
        user32.keybd_event(VK_SHIFT, shift_scan, KEYEVENTF_KEYUP, 0)
        time.sleep(0.04)

def run(args: dict, ctx: dict) -> str:
    try:
        # ১. স্ক্রিন ওয়েক করা
        ctypes.windll.user32.mouse_event(0x0001, 10, 10, 0, 0)
        time.sleep(0.3)

        # ২. স্পেস দিয়ে লকস্ক্রিন স্লাইড করা
        _press_vk(VK_SPACE)
        time.sleep(0.6)
        _press_vk(VK_SPACE)
        time.sleep(1.2)

        # ৩. পাসওয়ার্ড বক্সে ফোকাস আনতে স্ক্রিনে ক্লিক
        _click_center()
        time.sleep(0.3)

        # ৪. হার্ডওয়্যার স্ক্যান কোড দিয়ে পাসওয়ার্ড টাইপ
        for char in USER_KEY:
            _type_hardware_key(char)

        time.sleep(0.4)

        # ৫. এন্টার প্রেস
        _press_vk(VK_RETURN)

        return "ল্যাপটপ আনলক করে দিয়েছি, পাভেল স্যার!"
    except Exception as e:
        return f"ব্যর্থ হয়েছে: {e}"