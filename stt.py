"""
Speech-to-Text engines for MARK XL with instant Voice Barge-in support.

Whisper   – offline transcription via faster-whisper (VAD-buffered)
Vosk      – offline streaming transcription (lighter)
"""
import json
import numpy as np

# TTS থামানোর ফাংশন ইমপোর্ট
try:
    from core.tts import request_interrupt
except ImportError:
    def request_interrupt():
        pass


def _check_and_trigger_stop(text: str) -> bool:
    """মুখে স্টপ বা থামার কমান্ড পেলে তৎক্ষণাৎ অডিও থামিয়ে দেবে"""
    if not text:
        return False
    
    stop_words = [
        "থামো", "স্টপ", "stop", "থেমে যাও", "চুপ", "থাম",
        "বন্ধ করো", "গান বন্ধ করো", "চুপ করো"
    ]
    low_text = text.lower().strip()
    for word in stop_words:
        if word in low_text:
            print(f"\n[Voice Command] 🛑 মুখে স্টপ কমান্ড শনাক্ত হয়েছে ('{word}') — নেক্সাকে থামাচ্ছি!")
            request_interrupt()
            return True
    return False


class WhisperSTT:
    """Offline transcription using faster-whisper."""

    def __init__(self, model_name: str = "base", language: str | None = None):
        import os
        from faster_whisper import WhisperModel
        print(f"[STT] Loading Whisper '{model_name}'…")
        try:
            import torch
            device  = "cuda" if torch.cuda.is_available() else "cpu"
            compute = "float16" if device == "cuda" else "int8"
        except Exception:
            device, compute = "cpu", "int8"

        try:
            self._model = WhisperModel(model_name, device=device, compute_type=compute)
        except Exception as _first_err:
            _e = str(_first_err).lower()
            _offline_keywords = (
                "offline", "not found", "cache", "localentry",
                "does not exist", "outgoing", "local_files_only",
            )
            if any(k in _e for k in _offline_keywords):
                print(f"[STT] Whisper '{model_name}' not in local cache — downloading (one-time, internet required)…")
                os.environ.pop("HF_HUB_OFFLINE",       None)
                os.environ.pop("TRANSFORMERS_OFFLINE", None)
                os.environ.pop("HF_DATASETS_OFFLINE",  None)
                try:
                    self._model = WhisperModel(model_name, device=device, compute_type=compute)
                except Exception as _dl_err:
                    raise RuntimeError(
                        f"Whisper '{model_name}' model download failed.\n"
                        f"Internet access is required the first time to download the speech model (~75–290 MB).\n"
                        f"After the first download it runs fully offline.\n"
                        f"Details: {_dl_err}"
                    ) from _dl_err
            else:
                raise

        self._language = None if (not language or language.strip().lower() == "auto") else language.strip().lower()
        print(f"[STT] Whisper '{model_name}' ready ({device})")

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe a float32 mono 16 kHz numpy array. Returns transcript string."""
        try:
            segments, _ = self._model.transcribe(
                audio,
                language=self._language,
                beam_size=1,
                best_of=1,
                condition_on_previous_text=False,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 300},
            )
            text = " ".join(s.text for s in segments).strip()
            
            # ভয়েস স্টপ কমান্ড চেক
            if _check_and_trigger_stop(text):
                return ""  # এআই-এর কাছে বাড়তি টেক্সট যাবে না, শুধু ইন্টারাপ্ট হবে
                
            return text
        except Exception as e:
            print(f"[STT] Transcription error: {e}")
            raise


class VoskSTT:
    """Streaming transcription using Vosk."""

    def __init__(self, model_path: str | None = None, language: str = "en-us"):
        from vosk import Model, KaldiRecognizer
        print("[STT] Loading Vosk model…")
        if model_path:
            model = Model(model_path)
        else:
            lang  = language.strip().lower() if language and language.strip().lower() != "auto" else "en-us"
            model = Model(lang=lang)
        self._rec = KaldiRecognizer(model, 16000)
        print("[STT] Vosk ready.")

    def process_chunk(self, audio_bytes: bytes) -> tuple[str, bool]:
        """Feed raw int16 LE PCM bytes. Returns (text, is_final)."""
        if self._rec.AcceptWaveform(audio_bytes):
            result = json.loads(self._rec.Result())
            text = result.get("text", "")
            if _check_and_trigger_stop(text):
                return "", True
            return text, True
            
        partial = json.loads(self._rec.PartialResult())
        p_text = partial.get("partial", "")
        # পার্সিয়াল রেজাল্টেও যদি থামার কমান্ড আসে তবে আগেই থামাবে
        if _check_and_trigger_stop(p_text):
            return "", False
        return p_text, False