"""
Audio Engine
Captures 16000Hz, 16-bit Mono PCM audio from the microphone
in 40ms blocks (640 samples) and computes real-time RMS audio levels.
"""

import sounddevice as sd
import numpy as np
import threading
from typing import Callable, Optional

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 40  # 40ms audio chunks
BLOCK_SIZE = int(SAMPLE_RATE * (CHUNK_DURATION_MS / 1000.0))  # 640 samples

class AudioEngine:
    def __init__(self):
        self.stream: Optional[sd.InputStream] = None
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

                pcm_bytes = indata.tobytes()
                if self.on_chunk:
                    self.on_chunk(pcm_bytes)

                if self.on_level:
                    # Calculate RMS audio level (normalized 0.0 - 1.0)
                    samples = indata.astype(np.float32) / 32768.0
                    rms = np.sqrt(np.mean(samples ** 2))
                    level = min(1.0, float(rms * 5.0))
                    self.on_level(level)

            try:
                self.stream = sd.InputStream(
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
