import os
from pathlib import Path
from deepface import DeepFace

KNOWN_PATH = Path(__file__).resolve().parent.parent / "known_faces" / "pavel.jpg"

def check_if_pavel(frame_bytes: bytes) -> str:
    """ক্যামেরার ছবির সাথে pavel.jpg মিলিয়ে দেখে।"""
    if not KNOWN_PATH.exists() or not frame_bytes:
        return "unknown"

    temp_path = "temp_capture.jpg"
    try:
        with open(temp_path, "wb") as f:
            f.write(frame_bytes)

        result = DeepFace.verify(
            img1_path=temp_path,
            img2_path=str(KNOWN_PATH),
            model_name="VGG-Face",
            enforce_detection=False
        )

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if result.get("verified", False):
            return "pavel"
        else:
            return "stranger"
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return "unknown"