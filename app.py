"""
Antigravity Global Voice Typing (Hybrid Engine)
High-performance voice typing utility for Windows.
- Connects directly to the local Antigravity Language Server engine when available.
- Automatically falls back to universal speech recognition when Antigravity is not active.
- Global Hotkey: Alt + V (or Ctrl + Shift + V).
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import time
import threading
from typing import Optional, List

def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        log_path = os.path.join(current_dir, "app.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

log("Starting Voice Typing application (Hybrid Engine)...")

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

from antigravity_bridge import AntigravityBridge
from fallback_engine import FallbackEngine
from audio_engine import AudioEngine
from injector import TextInjector
from overlay_widget import OverlayWidget
from hotkey_service import HotkeyService

class VoiceTypingApp:
    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.bridge = AntigravityBridge()
        self.fallback = FallbackEngine()
        self.audio = AudioEngine()
        self.injector = TextInjector()
        
        self.overlay = OverlayWidget(hotkey_callback=self.on_hotkey_pressed)

        self.is_recording = False
        self.active_mode = "antigravity" # "antigravity" or "fallback"
        self.recorded_pcm_chunks: List[bytes] = []
        self.target_hwnd: Optional[int] = None
        self.accumulated_text = ""
        self.final_text_event = threading.Event()

        # System Tray Icon & Menu
        self.tray = QSystemTrayIcon(self._create_tray_icon(), self.qapp)
        self.tray.setToolTip("Antigravity Global Voice Typing (Alt + V)")
        self.tray.activated.connect(self._on_tray_activated)

        tray_menu = QMenu()
        toggle_action = QAction("🎙️ Toggle Voice Typing (Alt + V)", tray_menu)
        toggle_action.triggered.connect(self.on_hotkey_pressed)
        font = toggle_action.font()
        font.setBold(True)
        toggle_action.setFont(font)
        tray_menu.addAction(toggle_action)

        tray_menu.addSeparator()
        self.status_action = QAction("Status: Checking...", tray_menu)
        self.status_action.setEnabled(False)
        tray_menu.addAction(self.status_action)

        hotkey_info = QAction("Hotkey: Alt + V  (or Ctrl + Shift + V)", tray_menu)
        hotkey_info.setEnabled(False)
        tray_menu.addAction(hotkey_info)

        tray_menu.addSeparator()
        quit_action = QAction("Exit", tray_menu)
        quit_action.triggered.connect(self.quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.show()

        # Global Hotkey Hook Fallback
        self.hotkey_fallback = HotkeyService(callback=self.on_hotkey_pressed)
        self.hotkey_fallback.start()

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_bridge_status)
        self.check_timer.start(5000)
        self.check_bridge_status()

        QTimer.singleShot(600, self._show_welcome_balloon)

    def _show_welcome_balloon(self):
        port, _ = self.bridge.discover()
        mode_text = f"Antigravity Engine (Port {port})" if port else "Universal Speech Recognition"
        self.tray.showMessage(
            "🎙️ Voice Typing Ready",
            f"Engine: {mode_text}\nClick into any text field and press Alt + V to type.",
            QSystemTrayIcon.Information,
            2500
        )

    def _create_tray_icon(self) -> QIcon:
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Red glowing badge
        painter.setBrush(QColor(239, 68, 68))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 28, 28)

        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI Emoji", 14)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "🎙")
        painter.end()

        return QIcon(pixmap)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.on_hotkey_pressed()

    def check_bridge_status(self):
        port, _ = self.bridge.discover()
        if port:
            self.status_action.setText(f"Engine: Antigravity Connected (Port {port})")
        else:
            self.status_action.setText("Engine: Universal Speech Recognition")

    def on_hotkey_pressed(self):
        log(f"Hotkey triggered! is_recording={self.is_recording}")
        if not self.is_recording:
            self.target_hwnd = self.injector.get_current_window()
            log(f"Target window HWND: {self.target_hwnd}")
            self.start_recording()
        else:
            self.stop_recording_and_paste()

    def start_recording(self):
        self.is_recording = True
        self.accumulated_text = ""
        self.recorded_pcm_chunks = []
        self.final_text_event.clear()

        port, csrf = self.bridge.discover()
        if port:
            self.active_mode = "antigravity"
            log(f"Antigravity mode active (Port: {port}).")
            self.overlay.sig_show_state.emit('recording', "")

            def on_transcription(text: str, is_final: bool):
                if text:
                    log(f"Transcription: '{text}' (final: {is_final})")
                    if is_final:
                        if not text.endswith(" "):
                            text += " "
                        self.accumulated_text += text
                        self.overlay.sig_update_text.emit(self.accumulated_text, True)
                    else:
                        self.overlay.sig_update_text.emit(self.accumulated_text + text, False)

            def on_complete():
                log("Audio session stream finished.")
                self.final_text_event.set()

            def on_error(err):
                log(f"Audio stream error: {err}")
                self.overlay.sig_show_state.emit('error', f"Error: {err}")

            success = self.bridge.start_session(
                on_transcription=on_transcription,
                on_complete=on_complete,
                on_error=on_error
            )
            if not success:
                log("Bridge connection failed, falling back to universal engine.")
                self.active_mode = "fallback"
        else:
            self.active_mode = "fallback"
            log("Antigravity offline/not detected; Universal Engine active.")
            self.overlay.sig_show_state.emit('recording', "")

        def on_audio_chunk(pcm_bytes):
            if self.active_mode == "antigravity":
                self.bridge.send_audio_chunk(pcm_bytes)
            else:
                self.recorded_pcm_chunks.append(pcm_bytes)

        def on_audio_level(level):
            self.overlay.sig_update_level.emit(level)

        self.audio.start(on_chunk=on_audio_chunk, on_level=on_audio_level)
        log(f"Microphone recording started (Mode: {self.active_mode}).")

    def stop_recording_and_paste(self):
        self.is_recording = False
        log(f"Stopping recording (Mode: {self.active_mode})...")

        self.audio.stop()

        if self.active_mode == "antigravity":
            self.bridge.end_session()
            self.final_text_event.wait(timeout=1.2)
            result_text = self.accumulated_text.strip()
        else:
            # Fallback Engine Transcription
            self.overlay.sig_update_text.emit("Transcribing audio...", False)
            all_pcm = b"".join(self.recorded_pcm_chunks)
            result_text = self.fallback.transcribe_pcm(all_pcm) or ""
            result_text = result_text.strip()

        log(f"Final recognized text: '{result_text}'")
        self.overlay.sig_show_state.emit('pasting', result_text)

        if result_text:
            time.sleep(0.06)
            self.injector.paste_text(result_text, target_hwnd=self.target_hwnd)
            log("Text successfully pasted into target window.")

    def quit(self):
        log("Exiting application...")
        self.hotkey_fallback.stop()
        self.audio.stop()
        self.bridge.end_session()
        self.qapp.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    vt_app = VoiceTypingApp(app)
    log("VoiceTypingApp event loop running.")
    sys.exit(app.exec_())
