"""
Fallback Voice Engine
Antigravity kapalı olduğunda veya Antigravity yüklü olmayan herhangi bir bilgisayarda
ücretsiz, API anahtarsız ve evrensel ses tanıma motoru sağlar.
"""

import speech_recognition as sr
from typing import Optional

class FallbackEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_pcm(self, pcm16_bytes: bytes, sample_rate: int = 16000) -> Optional[str]:
        """Ham 16-bit Mono PCM ses verisini Türkçe metne dönüştürür."""
        if not pcm16_bytes:
            return None

        try:
            audio_data = sr.AudioData(pcm16_bytes, sample_rate, 2)
            # Google Web Speech API (Ücretsiz, API key istemez, yüksek Türkçe doğruluğu)
            text = self.recognizer.recognize_google(audio_data, language="tr-TR")
            return text
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[FallbackEngine] Tanıma hatası: {e}")
            return None
