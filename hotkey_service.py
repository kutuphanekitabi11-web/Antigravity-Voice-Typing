"""
Global Hotkey Service
Uses low-level keyboard hooks and pynput listeners to capture
Alt + V and Ctrl + Shift + V globally across all Windows applications.
"""

import time
from typing import Callable, Optional

class HotkeyService:
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self.last_trigger_time = 0.0
        self.debounce_sec = 0.35  # Prevent accidental double-trigger
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
            print(f"[Hotkey] Callback error: {e}")

    def start(self):
        if self.is_running:
            return
        self.is_running = True

        registered = False
        # Priority 1: keyboard library hook
        try:
            import keyboard
            keyboard.add_hotkey('alt+v', self._on_hotkey, suppress=False)
            print("[Hotkey] 'keyboard' Alt + V hook registered successfully.")
            registered = True
        except Exception as e:
            print(f"[Hotkey] 'keyboard' hook failed ({e}), falling back to pynput...")

        # Priority 2: pynput global hotkey listener
        try:
            import pynput.keyboard as pkb
            self.pynput_listener = pkb.GlobalHotKeys({
                '<alt>+v': self._on_hotkey,
                '<alt>+V': self._on_hotkey
            })
            self.pynput_listener.start()
            print("[Hotkey] 'pynput' Alt + V listener active.")
            registered = True
        except Exception as e:
            print(f"[Hotkey] 'pynput' init failed: {e}")

        if not registered:
            print("[Hotkey] WARNING: No hotkey backend could be initialized!")

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
