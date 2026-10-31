"""
Antigravity Global Voice Typing (Hybrid Engine)
Antigravity açıksa doğrudan yerel Language Server motorunu kullanır.
Antigravity kapalıysa veya yüklü değilse evrensel yedek motorla (SpeechRecognition) çalışır.
İndiren herkes her Windows bilgisayarda tek tıkla kullanabilir!
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

log("Uygulama başlatılıyor (Hibrit Motor)...")

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
        self.active_mode = "antigravity" # "antigravity" veya "fallback"
        self.recorded_pcm_chunks: List[bytes] = []
        self.target_hwnd: Optional[int] = None
        self.accumulated_text = ""
        self.final_text_event = threading.Event()

        # Sistem Tepsisi
        self.tray = QSystemTrayIcon(self._create_tray_icon(), self.qapp)
        self.tray.setToolTip("Antigravity Global Voice Typing (Alt + V)")
        self.tray.activated.connect(self._on_tray_activated)

        tray_menu = QMenu()
        toggle_action = QAction("🎙️ Kayıt Başlat / Durdur (Alt + V)", tray_menu)
        toggle_action.triggered.connect(self.on_hotkey_pressed)
        font = toggle_action.font()
        font.setBold(True)
        toggle_action.setFont(font)
        tray_menu.addAction(toggle_action)

        tray_menu.addSeparator()
        self.status_action = QAction("Durum: Kontrol ediliyor...", tray_menu)
        self.status_action.setEnabled(False)
        tray_menu.addAction(self.status_action)

        hotkey_info = QAction("Kısayol: Alt + V  (veya Ctrl + Shift + V)", tray_menu)
        hotkey_info.setEnabled(False)
        tray_menu.addAction(hotkey_info)

        tray_menu.addSeparator()
        quit_action = QAction("Çıkış", tray_menu)
        quit_action.triggered.connect(self.quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.show()

        # Global Hotkey Kancası
        self.hotkey_fallback = HotkeyService(callback=self.on_hotkey_pressed)
        self.hotkey_fallback.start()

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_bridge_status)
        self.check_timer.start(5000)
        self.check_bridge_status()

        QTimer.singleShot(500, self._show_welcome_balloon)

    def _show_welcome_balloon(self):
        port, _ = self.bridge.discover()
        mode_text = f"Antigravity Motoru (Port {port})" if port else "Evrensel Bağımsız Motor"
        self.tray.showMessage(
            "🎙️ Sesle Yazma Hazır",
            f"Mod: {mode_text}\nYazmak istediğiniz yere tıklayıp Alt + V tuşuna basın.",
            QSystemTrayIcon.Information,
            2500
        )

    def _create_tray_icon(self) -> QIcon:
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
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
            self.status_action.setText(f"Motor: Antigravity Bağlı (Port {port})")
        else:
            self.status_action.setText("Motor: Evrensel Bağımsız Mod")

    def on_hotkey_pressed(self):
        log(f"on_hotkey_pressed tetiklendi! is_recording={self.is_recording}")
        if not self.is_recording:
            self.target_hwnd = self.injector.get_current_window()
            log(f"Hedef pencere HWND: {self.target_hwnd}")
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
            log(f"Antigravity modu aktif (Port: {port}).")
            self.overlay.sig_show_state.emit('recording', "")

            def on_transcription(text: str, is_final: bool):
                if text:
                    log(f"Transkripsiyon: '{text}' (final: {is_final})")
                    if is_final:
                        if not text.endswith(" "):
                            text += " "
                        self.accumulated_text += text
                        self.overlay.sig_update_text.emit(self.accumulated_text, True)
                    else:
                        self.overlay.sig_update_text.emit(self.accumulated_text + text, False)

            def on_complete():
                log("Oturum akışı tamamlandı.")
                self.final_text_event.set()

            def on_error(err):
                log(f"Ses akışı hatası: {err}")
                self.overlay.sig_show_state.emit('error', f"Hata: {err}")

            success = self.bridge.start_session(
                on_transcription=on_transcription,
                on_complete=on_complete,
                on_error=on_error
            )
            if not success:
                log("Bridge başlatılamadı, yedek motora geçiliyor.")
                self.active_mode = "fallback"
        else:
            self.active_mode = "fallback"
            log("Antigravity kapalı/yok; Evrensel Yedek Motor devrede.")
            self.overlay.sig_show_state.emit('recording', "")

        def on_audio_chunk(pcm_bytes):
            if self.active_mode == "antigravity":
                self.bridge.send_audio_chunk(pcm_bytes)
            else:
                self.recorded_pcm_chunks.append(pcm_bytes)

        def on_audio_level(level):
            self.overlay.sig_update_level.emit(level)

        self.audio.start(on_chunk=on_audio_chunk, on_level=on_audio_level)
        log(f"Mikrofon kaydı başladı (Mod: {self.active_mode}).")

    def stop_recording_and_paste(self):
        self.is_recording = False
        log(f"Ses kaydı durduruluyor (Mod: {self.active_mode})...")

        self.audio.stop()

        if self.active_mode == "antigravity":
            self.bridge.end_session()
            self.final_text_event.wait(timeout=1.2)
            result_text = self.accumulated_text.strip()
        else:
            # Fallback Motoru Çözümlemesi
            self.overlay.sig_update_text.emit("Ses metne dönüştürülüyor...", False)
            all_pcm = b"".join(self.recorded_pcm_chunks)
            result_text = self.fallback.transcribe_pcm(all_pcm) or ""
            result_text = result_text.strip()

        log(f"Nihai metin: '{result_text}'")
        self.overlay.sig_show_state.emit('pasting', result_text)

        if result_text:
            time.sleep(0.06)
            self.injector.paste_text(result_text, target_hwnd=self.target_hwnd)
            log("Metin hedef pencereye yapıştırıldı.")

    def quit(self):
        log("Uygulama kapatılıyor...")
        self.hotkey_fallback.stop()
        self.audio.stop()
        self.bridge.end_session()
        self.qapp.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    vt_app = VoiceTypingApp(app)
    log("VoiceTypingApp döngüsü başladı.")
    sys.exit(app.exec_())
