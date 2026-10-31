"""
Floating Glassmorphic Overlay HUD
Sleek, transparent, patterned glassmorphic floating pill.
Never steals window focus (Qt.WindowDoesNotAcceptFocus).
Native Windows RegisterHotKey for global Alt + V and Ctrl + Shift + V.
"""

import sys
import ctypes
from ctypes import wintypes
import winsound
from PyQt5.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (
    QColor, QPainter, QBrush, QFont, QPen, QLinearGradient, QRadialGradient, QPainterPath
)

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
    """Dynamic audio waveform visualizer bars."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 26)
        self.level = 0.1
        self.bars = [0.15] * 5

    def set_level(self, level: float):
        self.level = max(0.08, min(1.0, level))
        import random
        self.bars = [
            max(0.12, min(1.0, self.level * (0.6 + random.random() * 0.85)))
            for _ in range(5)
        ]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bar_width = 4
        spacing = 4
        total_width = 5 * bar_width + 4 * spacing
        start_x = (self.width() - total_width) // 2
        h = self.height()

        for i, val in enumerate(self.bars):
            bar_h = max(5, int((h - 4) * val))
            y = (h - bar_h) // 2
            x = start_x + i * (bar_width + spacing)
            
            bar_grad = QLinearGradient(x, y, x, y + bar_h)
            bar_grad.setColorAt(0.0, QColor(248, 113, 113))
            bar_grad.setColorAt(1.0, QColor(225, 29, 72))
            
            painter.setBrush(QBrush(bar_grad))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_h, 2, 2)


class PatternedPillContainer(QWidget):
    """
    Custom container that paints a sleek dark glassmorphic pill
    with an intricate micro-dot mesh pattern and soft glowing rim.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        w = float(rect.width())
        h = float(rect.height())
        radius = 24.0

        path = QPainterPath()
        path.addRoundedRect(1.0, 1.0, w - 2.0, h - 2.0, radius, radius)

        # 1. Base Obsidian Glass Background
        base_grad = QLinearGradient(0, 0, 0, h)
        base_grad.setColorAt(0.0, QColor(15, 18, 28, 245))
        base_grad.setColorAt(1.0, QColor(9, 11, 18, 250))
        painter.fillPath(path, base_grad)

        # Clip subsequent pattern inside rounded pill
        painter.save()
        painter.setClipPath(path)

        # 2. Ambient Cyan/Indigo Radial Mesh Glow
        glow = QRadialGradient(w * 0.25, 0, w * 0.6)
        glow.setColorAt(0.0, QColor(99, 102, 241, 32))
        glow.setColorAt(0.5, QColor(56, 189, 248, 16))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(rect, glow)

        # 3. Geometric Micro-Dot Matrix Pattern
        dot_pen = QPen(QColor(255, 255, 255, 14))
        dot_pen.setWidth(1)
        painter.setPen(dot_pen)
        grid_step = 11
        for x in range(grid_step // 2, int(w), grid_step):
            for y in range(grid_step // 2, int(h), grid_step):
                painter.drawPoint(x, y)

        # 4. Subtle Diagonal Cyber Cross-Hatch Lines
        line_pen = QPen(QColor(255, 255, 255, 6))
        line_pen.setStyle(Qt.DotLine)
        painter.setPen(line_pen)
        for d in range(-int(h), int(w), 32):
            painter.drawLine(d, 0, d + int(h), int(h))

        painter.restore()

        # 5. Frosted Glass Rim Highlight
        border_grad = QLinearGradient(0, 0, 0, h)
        border_grad.setColorAt(0.0, QColor(255, 255, 255, 75))
        border_grad.setColorAt(0.35, QColor(255, 255, 255, 30))
        border_grad.setColorAt(1.0, QColor(255, 255, 255, 12))

        border_pen = QPen(QBrush(border_grad), 1.2)
        painter.setPen(border_pen)
        painter.drawPath(path)


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
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # Patterned Glassmorphic Container
        self.container = PatternedPillContainer(self)
        self.container.setMinimumHeight(64)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

        # Symmetrical 3-Column Layout: Left (54px), Center (Flexible), Right (54px)
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(8)

        # 1. Left Symmetrical Box (Fixed 54px)
        self.left_box = QWidget(self.container)
        self.left_box.setFixedSize(54, 44)
        self.left_box.setStyleSheet("background: transparent; border: none;")
        left_layout = QHBoxLayout(self.left_box)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignCenter)

        self.lbl_icon = QLabel("🎙️", self.left_box)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("font-size: 21px; background: transparent; border: none;")
        left_layout.addWidget(self.lbl_icon)
        container_layout.addWidget(self.left_box)

        # 2. Center Text Box (Symmetrically centered)
        self.center_box = QWidget(self.container)
        self.center_box.setStyleSheet("background: transparent; border: none;")
        center_layout = QVBoxLayout(self.center_box)
        center_layout.setSpacing(2)
        center_layout.setContentsMargins(4, 0, 4, 0)
        center_layout.setAlignment(Qt.AlignCenter)

        self.lbl_status = QLabel("LISTENING...", self.center_box)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("""
            color: #F87171;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            background: transparent;
            border: none;
        """)
        center_layout.addWidget(self.lbl_status)

        self.lbl_text = QLabel("Speak now, transcribing in real-time...", self.center_box)
        self.lbl_text.setAlignment(Qt.AlignCenter)
        self.lbl_text.setStyleSheet("""
            color: #F3F4F6;
            font-size: 14px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setMaximumWidth(520)
        center_layout.addWidget(self.lbl_text)

        container_layout.addWidget(self.center_box, 1)

        # 3. Right Symmetrical Box (Fixed 54px)
        self.right_box = QWidget(self.container)
        self.right_box.setFixedSize(54, 44)
        self.right_box.setStyleSheet("background: transparent; border: none;")
        right_layout = QHBoxLayout(self.right_box)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignCenter)

        self.visualizer = VisualizerWidget(self.right_box)
        right_layout.addWidget(self.visualizer)

        self.lbl_right_badge = QLabel("✓", self.right_box)
        self.lbl_right_badge.setAlignment(Qt.AlignCenter)
        self.lbl_right_badge.setStyleSheet("""
            color: #34D399;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        self.lbl_right_badge.setVisible(False)
        right_layout.addWidget(self.lbl_right_badge)

        container_layout.addWidget(self.right_box)

        main_layout.addWidget(self.container)
        self.adjustSize()

    def init_native_hotkeys(self):
        """Register global Windows hotkeys (Alt + V and Ctrl + Shift + V)."""
        hwnd = int(self.winId())
        r1 = user32.RegisterHotKey(hwnd, HOTKEY_ID_ALTV, MOD_ALT | MOD_NOREPEAT, VK_V)
        if not r1:
            r1 = user32.RegisterHotKey(hwnd, HOTKEY_ID_ALTV, MOD_ALT, VK_V)
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
        self.lbl_status.setText("LISTENING · Press Alt + V to finish")
        self.lbl_status.setStyleSheet("""
            color: #F87171;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.0px;
            background: transparent;
            border: none;
        """)
        self.lbl_text.setText("Speak now, transcribing in real-time...")
        self.lbl_text.setStyleSheet("""
            color: #9CA3AF;
            font-size: 14px;
            background: transparent;
            border: none;
        """)
        self.visualizer.setVisible(True)
        self.lbl_right_badge.setVisible(False)
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
        self.lbl_status.setText("TEXT INSERTED")
        self.lbl_status.setStyleSheet("""
            color: #34D399;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            background: transparent;
            border: none;
        """)
        disp_text = final_text.strip() if final_text and final_text.strip() else "(No speech detected)"
        # Cap display length for HUD pill aesthetics while full text is safely pasted
        if len(disp_text) > 85:
            disp_text = disp_text[:82] + "..."
        self.lbl_text.setText(disp_text)
        self.lbl_text.setStyleSheet("""
            color: #F9FAFB;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        self.visualizer.setVisible(False)
        self.lbl_right_badge.setText("✓")
        self.lbl_right_badge.setStyleSheet("""
            color: #34D399;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        self.lbl_right_badge.setVisible(True)

        self.reposition()
        self.setVisible(True)
        self.show()
        self.raise_()

        try:
            winsound.Beep(900, 70)
        except Exception:
            pass

        self.fade_timer.start(1800)

    def show_error(self, message: str):
        self.lbl_icon.setText("⚠️")
        self.lbl_status.setText("INFO")
        self.lbl_status.setStyleSheet("""
            color: #F59E0B;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.0px;
            background: transparent;
            border: none;
        """)
        self.lbl_text.setText(message)
        self.lbl_text.setStyleSheet("""
            color: #F9FAFB;
            font-size: 13px;
            background: transparent;
            border: none;
        """)
        self.visualizer.setVisible(False)
        self.lbl_right_badge.setVisible(False)
        self.reposition()
        self.setVisible(True)
        self.show()
        self.raise_()
        self.fade_timer.start(3500)

    def hide_overlay(self):
        self.hide()

    def _on_update_text(self, text: str, is_final: bool):
        if text.strip():
            display = text.strip()
            # For long continuous dictation, show ellipsis and tail in HUD so pill maintains sleek proportions
            if len(display) > 130:
                display = "..." + display[-125:]
            self.lbl_text.setText(display)
            self.lbl_text.setStyleSheet("""
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                border: none;
            """)
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
