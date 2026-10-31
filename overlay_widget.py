"""
Floating Overlay UI
Kullanıcı kayıt yaparken ekranın üst-orta kısmında beliren şık, saydam (glassmorphism),
odağı ASLA çalmayan (WindowDoesNotAcceptFocus) modern dikte hapı.
Windows RegisterHotKey ile native WM_HOTKEY mesajlarını doğrudan yakalar.
"""

import sys
import ctypes
from ctypes import wintypes
import winsound
from PyQt5.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QBrush, QFont

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
VK_V = 0x56
WM_HOTKEY = 0x0312

HOTKEY_ID_ALTV = 1001
HOTKEY_ID_CTRLSHIFTV = 1002

class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(65, 26)
        self.level = 0.1
        self.bars = [0.1] * 5

    def set_level(self, level: float):
        self.level = max(0.08, min(1.0, level))
        import random
        self.bars = [
            max(0.12, min(1.0, self.level * (0.6 + random.random() * 0.8)))
            for _ in range(5)
        ]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bar_width = 4
        spacing = 5
        start_x = 10
        h = self.height()

        for i, val in enumerate(self.bars):
            bar_h = max(5, int((h - 4) * val))
            y = (h - bar_h) // 2
            x = start_x + i * (bar_width + spacing)
            
            painter.setBrush(QBrush(QColor(239, 68, 68, 230)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_h, 2, 2)


class OverlayWidget(QWidget):
    sig_update_text = pyqtSignal(str, bool)
    sig_update_level = pyqtSignal(float)
    sig_show_state = pyqtSignal(str, str) # state, text

    def __init__(self, hotkey_callback=None):
        super().__init__()
        self.hotkey_callback = hotkey_callback
        self.init_ui()
        self.init_native_hotkeys()

        self.fade_timer = QTimer(self)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self.hide_overlay)

        self.sig_update_text.connect(self._on_update_text)
        self.sig_update_level.connect(self._on_update_level)
        self.sig_show_state.connect(self._on_show_state)

    def init_ui(self):
        # Pencere bayrakları: Odağı asla çalma, üstte kal, çerçevesiz, görev çubuğunda görünme
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Arka plan kutusu (Modern Koyu Cam Efekti)
        self.container = QWidget(self)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 17, 23, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 20px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 210))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(18, 10, 20, 10)
        container_layout.setSpacing(12)

        self.lbl_icon = QLabel("🎙️", self)
        self.lbl_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        container_layout.addWidget(self.lbl_icon)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_status = QLabel("DİNLENİYOR...", self)
        self.lbl_status.setStyleSheet("""
            color: #EF4444;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.8px;
            background: transparent;
            border: none;
        """)
        text_layout.addWidget(self.lbl_status)

        self.lbl_text = QLabel("Konuşun, sesiniz yazıya dökülüyor...", self)
        self.lbl_text.setStyleSheet("""
            color: #F9FAFB;
            font-size: 14px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setMaximumWidth(520)
        text_layout.addWidget(self.lbl_text)

        container_layout.addLayout(text_layout)

        self.visualizer = VisualizerWidget(self)
        container_layout.addWidget(self.visualizer)

        main_layout.addWidget(self.container)
        self.adjustSize()

    def init_native_hotkeys(self):
        """Windows RegisterHotKey ile Qt penceresine Alt + V ve Ctrl + Shift + V bağlar."""
        hwnd = int(self.winId())
        # Alt + V
        r1 = user32.RegisterHotKey(hwnd, HOTKEY_ID_ALTV, MOD_ALT | MOD_NOREPEAT, VK_V)
        if not r1:
            r1 = user32.RegisterHotKey(hwnd, HOTKEY_ID_ALTV, MOD_ALT, VK_V)
        # Ctrl + Shift + V (Alternatif/Yedek kısayol)
        r2 = user32.RegisterHotKey(hwnd, HOTKEY_ID_CTRLSHIFTV, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_V)

        print(f"[Overlay] Native Hotkeys Registered: Alt+V={bool(r1)}, Ctrl+Shift+V={bool(r2)}")

    def nativeEvent(self, eventType, message):
        try:
            msg = wintypes.MSG.from_address(message.__int__())
            if msg.message == WM_HOTKEY:
                if msg.wParam in (HOTKEY_ID_ALTV, HOTKEY_ID_CTRLSHIFTV):
                    if self.hotkey_callback:
                        self.hotkey_callback()
                        return True, 0
        except Exception:
            pass
        return super().nativeEvent(eventType, message)

    def show_recording(self):
        self.fade_timer.stop()
        self.lbl_icon.setText("🎙️")
        self.lbl_status.setText("DİNLENİYOR · (Bitirmek için tekrar Alt + V)")
        self.lbl_status.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: 800; background: transparent; border: none;")
        self.lbl_text.setText("Konuşun, sesiniz anında metne dökülecek...")
        self.lbl_text.setStyleSheet("color: #9CA3AF; font-size: 14px; background: transparent; border: none;")
        self.visualizer.setVisible(True)
        self.reposition()
        self.setVisible(True)
        self.show()
        self.raise_()
        
        try:
            winsound.Beep(1200, 70)
        except Exception:
            pass

    def show_pasting(self, final_text: str):
        self.lbl_icon.setText("✍️")
        self.lbl_status.setText("METİN YAZILDI")
        self.lbl_status.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 800; background: transparent; border: none;")
        disp_text = final_text if final_text else "(Ses algılanamadı)"
        if len(disp_text) > 85:
            disp_text = disp_text[:82] + "..."
        self.lbl_text.setText(disp_text)
        self.lbl_text.setStyleSheet("color: #F9FAFB; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        self.visualizer.setVisible(False)
        self.reposition()
        self.setVisible(True)
        self.show()
        self.raise_()

        try:
            winsound.Beep(900, 70)
        except Exception:
            pass

        self.fade_timer.start(1600)

    def show_error(self, message: str):
        self.lbl_icon.setText("⚠️")
        self.lbl_status.setText("BİLGİ")
        self.lbl_status.setStyleSheet("color: #F59E0B; font-size: 11px; font-weight: 800; background: transparent; border: none;")
        self.lbl_text.setText(message)
        self.lbl_text.setStyleSheet("color: #F9FAFB; font-size: 13px; background: transparent; border: none;")
        self.visualizer.setVisible(False)
        self.reposition()
        self.setVisible(True)
        self.show()
        self.raise_()
        self.fade_timer.start(3500)

    def hide_overlay(self):
        self.hide()

    def _on_update_text(self, text: str, is_final: bool):
        if text.strip():
            self.lbl_text.setText(text)
            self.lbl_text.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 500; background: transparent; border: none;")
            self.reposition()

    def _on_update_level(self, level: float):
        self.visualizer.set_level(level)

    def _on_show_state(self, state: str, text: str):
        if state == 'recording':
            self.show_recording()
        elif state == 'pasting':
            self.show_pasting(text)
        elif state == 'error':
            self.show_error(text)

    def reposition(self):
        self.adjustSize()
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
            y = screen_geo.y() + 70
            self.move(x, y)
