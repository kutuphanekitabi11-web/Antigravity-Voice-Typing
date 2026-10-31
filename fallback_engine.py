"""
Universal Fallback Voice Engine
Provides free, API-keyless, standalone speech recognition when
Antigravity is inactive or on systems without Antigravity installed.
"""

import speech_recognition as sr
from typing import Optional

class FallbackEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_pcm(self, pcm16_bytes: bytes, sample_rate: int = 16000) -> Optional[str]:
        """Converts raw 16-bit Mono PCM audio bytes to text."""
        if not pcm16_bytes:
            return None

        try:
            audio_data = sr.AudioData(pcm16_bytes, sample_rate, 2)
            # Google Web Speech API (Free, zero API key required, high accuracy)
            text = self.recognizer.recognize_google(audio_data, language="tr-TR")
            return text
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[FallbackEngine] Recognition error: {e}")
            return None
