"""
Text-to-Speech engines for MARK XL with instant interruption support.
"""
from __future__ import annotations

import asyncio
import os
import queue as _queue
import threading
import time
from typing import Callable, Optional

import numpy as np
import sounddevice as sd

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# ---------------------------------------------------------------------------
# Global Interruption Flag
# ---------------------------------------------------------------------------
_interrupt_requested = threading.Event()

def request_interrupt() -> None:
    """যেকোনো জায়গা থেকে এটি কল করলে চলমান অডিও সাথে সাথে বন্ধ হবে"""
    _interrupt_requested.set()
    sd.stop()

# ---------------------------------------------------------------------------
# Audio playback helpers (Non-blocking & Interruptible)
# ---------------------------------------------------------------------------

def _to_numpy(samples) -> np.ndarray:
    if hasattr(samples, "detach"):
        t = samples.detach().cpu().float()
        try:
            return t.numpy()
        except RuntimeError:
            return np.asarray(t.tolist(), dtype=np.float32)
    return np.asarray(samples, dtype=np.float32)


def _compress_silence(
    arr: np.ndarray,
    sample_rate: int = 24_000,
    max_silence_ms: int = 500,
    threshold: float = 0.003,
) -> np.ndarray:
    max_samp = int(max_silence_ms * sample_rate / 1000)
    frame_len = 240
    out: list[np.ndarray] = []
    silent_acc = 0

    for i in range(0, len(arr), frame_len):
        chunk = arr[i : i + frame_len]
        if np.sqrt(np.mean(chunk ** 2) + 1e-12) < threshold:
            silent_acc += len(chunk)
            if silent_acc <= max_samp:
                out.append(chunk)
        else:
            silent_acc = 0
            out.append(chunk)

    return np.concatenate(out) if out else arr


def _play_np(samples, sample_rate: int) -> None:
    """Interrupt-safe playback loop."""
    data = _to_numpy(samples)
    sd.play(data, sample_rate)
    
    # sd.wait() এর পরিবর্তে লুপ দিয়ে প্রতি ৫০ মিলি-সেকেন্ডে ইন্টারাপ্ট চেক করা
    while sd.get_stream() and sd.get_stream().active:
        if _interrupt_requested.is_set():
            sd.stop()
            break
        time.sleep(0.05)


def _play_audio_bytes(audio_bytes: bytes) -> None:
    """Decode MP3/WAV/OGG bytes and play with interrupt support."""
    import miniaudio
    decoded = miniaudio.decode(
        audio_bytes,
        output_format=miniaudio.SampleFormat.FLOAT32,
        nchannels=1,
    )
    samples = np.array(decoded.samples, dtype=np.float32)
    _play_np(samples, decoded.sample_rate)


# ---------------------------------------------------------------------------
# Engines
# ---------------------------------------------------------------------------

class EdgeTTSEngine:
    def __init__(self, voice: str = "bn-BD-NabanitaNeural"):
        self.voice = voice

    def speak(self, text: str) -> None:
        if _interrupt_requested.is_set():
            return
            
        loop = asyncio.new_event_loop()
        try:
            audio_bytes = loop.run_until_complete(self._synth(text))
        finally:
            loop.close()
            
        if audio_bytes and not _interrupt_requested.is_set():
            _play_audio_bytes(audio_bytes)

    async def _synth(self, text: str) -> bytes:
        import edge_tts
        comm = edge_tts.Communicate(text, self.voice)
        buf = bytearray()
        async for chunk in comm.stream():
            if _interrupt_requested.is_set():
                break
            if chunk["type"] == "audio":
                buf.extend(chunk["data"])
        return bytes(buf)


# Kokoro helpers & Engines
_KOKORO_LANG_CODES = {
    "a": "a", "b": "b", "j": "j", "z": "z", "s": "s",
    "f": "f", "h": "h", "i": "i", "p": "p", "r": "r", "e": "e"
}

def _import_kokoro_pipeline():
    from kokoro import KPipeline
    return KPipeline

class KokoroTTSEngine:
    def __init__(self, voice: str = "af_heart", speed: float = 1.0):
        self.voice = voice
        self.speed = speed
        self._pipeline = None
        self._lock = threading.Lock()
        self._init()

    @property
    def _lang_code(self) -> str:
        prefix = self.voice[0].lower() if self.voice else "a"
        return _KOKORO_LANG_CODES.get(prefix, "a")

    def _init(self) -> None:
        if self._pipeline is not None:
            return
        lang = self._lang_code
        try:
            KPipeline = _import_kokoro_pipeline()
            self._pipeline = KPipeline(lang_code=lang, device="cpu")
        except Exception as e:
            print(f"[TTS] Kokoro init error: {e}")

    def speak(self, text: str) -> None:
        with self._lock:
            if self._pipeline is None:
                self._init()

        audio_q: "_queue.Queue[np.ndarray | None]" = _queue.Queue(maxsize=4)

        def _synth():
            try:
                for _, _, audio in self._pipeline(text, voice=self.voice, speed=self.speed):
                    if _interrupt_requested.is_set():
                        break
                    if audio is not None:
                        arr = _to_numpy(audio)
                        arr = _compress_silence(arr)
                        if arr.size > 0:
                            audio_q.put(arr)
            except Exception:
                pass
            finally:
                audio_q.put(None)

        synth_thread = threading.Thread(target=_synth, daemon=True)
        synth_thread.start()

        while True:
            if _interrupt_requested.is_set():
                sd.stop()
                break
            try:
                arr = audio_q.get(timeout=0.1)
                if arr is None:
                    break
                _play_np(arr, 24000)
            except _queue.Empty:
                if not synth_thread.is_alive():
                    break

        synth_thread.join()


class ElevenLabsTTSEngine:
    def __init__(self, api_key: str, voice_id: str = "pNInz6obpgDQGcFmaJgB"):
        self.api_key = api_key
        self.voice_id = voice_id

    def speak(self, text: str) -> None:
        if _interrupt_requested.is_set():
            return
        import requests
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
            json=payload, headers=headers, timeout=30,
        )
        resp.raise_for_status()
        if not _interrupt_requested.is_set():
            _play_audio_bytes(resp.content)


# ---------------------------------------------------------------------------
# Thread-safe player wrapper
# ---------------------------------------------------------------------------

class TTSPlayer:
    def __init__(self, engine):
        self._engine = engine
        self._playing = False
        self._lock = threading.Lock()

    @property
    def is_playing(self) -> bool:
        return self._playing

    def speak(
        self,
        text: str,
        on_start: Optional[Callable] = None,
        on_done: Optional[Callable] = None,
    ) -> None:
        try:
            _interrupt_requested.clear()
            with self._lock:
                self._playing = True
            if on_start:
                on_start()
            self._engine.speak(text)
        except Exception as e:
            print(f"[TTS] Error: {e}")
        finally:
            with self._lock:
                self._playing = False
            if on_done:
                on_done()

    def stop(self) -> None:
        """কল করামাত্রই অডিও বন্ধ হবে"""
        request_interrupt()
        with self._lock:
            self._playing = False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_tts_player(config: dict) -> TTSPlayer:
    engine_name = config.get("tts_engine", "edgetts").lower()
    if engine_name == "kokoro":
        voice = config.get("tts_voice", "af_heart")
        speed = float(config.get("tts_speed", 1.0))
        engine = KokoroTTSEngine(voice=voice, speed=speed)
    elif engine_name == "elevenlabs":
        api_key = config.get("elevenlabs_api_key", "")
        voice_id = config.get("tts_voice", "pNInz6obpgDQGcFmaJgB")
        engine = ElevenLabsTTSEngine(api_key=api_key, voice_id=voice_id)
    else:
        # ডিফল্ট মিষ্টি কণ্ঠ
        voice = config.get("tts_voice", "bn-BD-NabanitaNeural")
        engine = EdgeTTSEngine(voice=voice)
    return TTSPlayer(engine)