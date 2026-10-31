"""
Global Hotkey Service
keyboard ve pynput kütüphanelerini birlikte kullanarak tüm Windows ortamında
herhangi bir pencerede Alt + V kısayolunu anında ve güvenilir şekilde yakalar.
"""

import time
from typing import Callable, Optional

class HotkeyService:
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self.last_trigger_time = 0.0
        self.debounce_sec = 0.35  # Çift tetiklemeyi önleme
        self.is_running = False
        self.pynput_listener = None

    def _on_hotkey(self):
        now = time.time()
        if now - self.last_trigger_time < self.debounce_sec:
            return
        self.last_trigger_time = now
        try:
            self.callback()
        except Exception as e:
            print(f"[Hotkey] Callback çalıştırma hatası: {e}")

    def start(self):
        if self.is_running:
            return
        self.is_running = True

        registered = False
        # 1. Öncelik: keyboard kütüphanesi (düşük seviye Windows klavye kancası)
        try:
            import keyboard
            keyboard.add_hotkey('alt+v', self._on_hotkey, suppress=False)
            print("[Hotkey] 'keyboard' ile Alt + V başarıyla bağlandı.")
            registered = True
        except Exception as e:
            print(f"[Hotkey] 'keyboard' başlatılamadı ({e}), pynput deneniyor...")

        # 2. Öncelik / Yedek: pynput kütüphanesi
        try:
            import pynput.keyboard as pkb
            self.pynput_listener = pkb.GlobalHotKeys({
                '<alt>+v': self._on_hotkey,
                '<alt>+V': self._on_hotkey
            })
            self.pynput_listener.start()
            print("[Hotkey] 'pynput' ile Alt + V dinleyici aktif.")
            registered = True
        except Exception as e:
            print(f"[Hotkey] 'pynput' başlatılamadı: {e}")

        if not registered:
            print("[Hotkey] UYARI: Hiçbir kısayol motoru başlatılamadı!")

    def stop(self):
        self.is_running = False
        try:
            import keyboard
            keyboard.remove_hotkey('alt+v')
        except Exception:
            pass

        if self.pynput_listener:
            try:
                self.pynput_listener.stop()
            except Exception:
                pass
            self.pynput_listener = None
