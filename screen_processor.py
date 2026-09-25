import os
import time
import pyautogui
import cv2
import numpy as np

TOOL = {
    "name": "screen_processor",
    "description": "Captures the screen or webcam image for visual analysis.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "angle": {"type": "STRING", "description": "'screen' to capture display, 'camera' for webcam. Default: 'screen'"},
            "text":  {"type": "STRING", "description": "The question or instruction about the captured image"}
        },
        "required": ["text"]
    }
}

def _capture_screen() -> tuple[bytes, str]:
    """Captures the main display and returns JPEG bytes and mime type."""
    try:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        _, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        return encoded.tobytes(), "image/jpeg"
    except Exception as e:
        print(f"[ScreenCapture Error] {e}")
        return b"", "image/jpeg"

def _capture_camera() -> tuple[bytes, str]:
    """Captures a frame from the webcam and returns JPEG bytes and mime type."""
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return b"", "image/jpeg"
        
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return b"", "image/jpeg"
            
        _, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        return encoded.tobytes(), "image/jpeg"
    except Exception as e:
        print(f"[CameraCapture Error] {e}")
        return b"", "image/jpeg"

def run(args, context=None):
    angle = args.get("angle", "screen").lower()
    if angle == "camera":
        b, m = _capture_camera()
        return f"Camera captured {len(b)} bytes." if b else "Failed to capture camera."
    else:
        b, m = _capture_screen()
        return f"Screen captured {len(b)} bytes." if b else "Failed to capture screen."