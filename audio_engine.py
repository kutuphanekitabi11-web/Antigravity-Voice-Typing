"""
Audio Engine
Captures 16000Hz, 16-bit Mono PCM audio from the microphone
in 40ms blocks (640 samples) and computes real-time RMS audio levels.
Optimized for zero-numpy footprint to eliminate BLAS thread pool & DLL overhead.
"""

import sounddevice as sd
import threading
import struct
import math
from typing import Callable, Optional

try:
    import audioop
    _HAVE_AUDIOOP = True
except ImportError:
    _HAVE_AUDIOOP = False

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 40  # 40ms audio chunks
BLOCK_SIZE = int(SAMPLE_RATE * (CHUNK_DURATION_MS / 1000.0))  # 640 samples


def compute_rms_level(pcm_bytes: bytes) -> float:
    """Computes normalized RMS audio level (0.0 to 1.0) without numpy."""
    if not pcm_bytes:
        return 0.0

    count = len(pcm_bytes) // 2
    if count <= 0:
        return 0.0

    # Ensure buffer is aligned to 16-bit boundaries (discard any odd trailing byte)
    valid_len = count * 2
    if len(pcm_bytes) != valid_len:
        pcm_bytes = pcm_bytes[:valid_len]

    if _HAVE_AUDIOOP:
        try:
            # audioop.rms calculates root-mean-square for 16-bit signed PCM
            rms = audioop.rms(pcm_bytes, 2)
            # Normalize to 0.0 - 1.0 (with 5x gain factor matching previous behavior)
            return min(1.0, (rms / 32768.0) * 5.0)
        except Exception:
            pass

    # Pure Python fallback using struct and math
    try:
        shorts = struct.unpack(f'<{count}h', pcm_bytes)
        sum_sq = sum(s * s for s in shorts)
        rms = math.sqrt(sum_sq / count) / 32768.0
        return min(1.0, rms * 5.0)
    except Exception:
        return 0.0


class AudioEngine:
    def __init__(self):
        self.stream: Optional[sd.RawInputStream] = None
        self.is_recording = False
        self.on_chunk: Optional[Callable[[bytes], None]] = None
        self.on_level: Optional[Callable[[float], None]] = None
        self._lock = threading.Lock()

    def start(
        self,
        on_chunk: Callable[[bytes], None],
        on_level: Optional[Callable[[float], None]] = None
    ) -> bool:
        with self._lock:
            if self.is_recording:
                return True

            self.on_chunk = on_chunk
            self.on_level = on_level

            def audio_callback(indata, frames, time_info, status):
                if not self.is_recording:
                    return

                try:
                    # In RawInputStream, indata is a buffer/bytes-like object containing raw PCM bytes
                    pcm_bytes = bytes(indata)
                    cb_chunk = self.on_chunk
                    if cb_chunk:
                        cb_chunk(pcm_bytes)

                    cb_level = self.on_level
                    if cb_level:
                        level = compute_rms_level(pcm_bytes)
                        cb_level(level)
                except Exception:
                    pass

            try:
                self.stream = sd.RawInputStream(
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype='int16',
                    blocksize=BLOCK_SIZE,
                    callback=audio_callback
                )
                self.stream.start()
                self.is_recording = True
                return True
            except Exception as e:
                print(f"[AudioEngine] Microphone initialization error: {e}")
                if self.stream:
                    try:
                        self.stream.close()
                    except Exception:
                        pass
                self.stream = None
                self.is_recording = False
                return False

    def stop(self):
        with self._lock:
            if not self.is_recording:
                return

            self.is_recording = False
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None
            self.on_chunk = None
            self.on_level = None
