"""
Script to generate high-resolution showcase graphic cards for README.md
Renders pixel-perfect visual mockups of the HUD in various operational states.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath
)
from PyQt5.QtCore import Qt, QRectF

app = QApplication(sys.argv)

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(output_dir, exist_ok=True)

W = 880
H = 260

def draw_pill(painter, x, y, width, height, icon, status_text, status_color, body_text, right_type="waveform", wave_bars=None):
    """Draws the patterned glassmorphic floating pill."""
    radius = 22.0
    pill_rect = QRectF(x, y, width, height)
    path = QPainterPath()
    path.addRoundedRect(pill_rect, radius, radius)

    # Base gradient
    base_grad = QLinearGradient(x, y, x, y + height)
    base_grad.setColorAt(0.0, QColor(15, 18, 28, 245))
    base_grad.setColorAt(1.0, QColor(9, 11, 18, 252))
    painter.fillPath(path, base_grad)

    painter.save()
    painter.setClipPath(path)

    # Radial ambient glow
    glow = QRadialGradient(x + width * 0.25, y, width * 0.6)
    glow.setColorAt(0.0, QColor(99, 102, 241, 35))
    glow.setColorAt(0.5, QColor(56, 189, 248, 18))
    glow.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.fillRect(pill_rect.toRect(), glow)

    # Micro-dot matrix pattern
    dot_pen = QPen(QColor(255, 255, 255, 18))
    dot_pen.setWidth(1)
    painter.setPen(dot_pen)
    grid = 11
    for px in range(int(x) + grid // 2, int(x + width), grid):
        for py in range(int(y) + grid // 2, int(y + height), grid):
            painter.drawPoint(px, py)

    painter.restore()

    # Glass highlight rim
    rim_grad = QLinearGradient(x, y, x, y + height)
    rim_grad.setColorAt(0.0, QColor(255, 255, 255, 75))
    rim_grad.setColorAt(0.35, QColor(255, 255, 255, 30))
    rim_grad.setColorAt(1.0, QColor(255, 255, 255, 12))
    rim_pen = QPen(QBrush(rim_grad), 1.2)
    painter.setPen(rim_pen)
    painter.drawPath(path)

    # Left Box (Fixed 54px)
    icon_rect = QRectF(x, y, 54, height)
    painter.setFont(QFont("Segoe UI Emoji", 16))
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(icon_rect, Qt.AlignCenter, icon)

    # Right Box (Fixed 54px)
    right_rect = QRectF(x + width - 54, y, 54, height)
    if right_type == "waveform":
        bars = wave_bars or [0.3, 0.7, 0.9, 0.5, 0.4]
        bar_w = 3.5
        spacing = 3.5
        tot_w = len(bars) * bar_w + (len(bars) - 1) * spacing
        bx_start = right_rect.x() + (right_rect.width() - tot_w) / 2
        for idx, val in enumerate(bars):
            bh = max(5, int((height - 18) * val))
            by = y + (height - bh) / 2
            bx = bx_start + idx * (bar_w + spacing)
            b_grad = QLinearGradient(bx, by, bx, by + bh)
            b_grad.setColorAt(0.0, QColor(248, 113, 113))
            b_grad.setColorAt(1.0, QColor(225, 29, 72))
            painter.setBrush(QBrush(b_grad))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(bx, by, bar_w, bh), 1.5, 1.5)
    elif right_type == "badge":
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.setPen(QColor(52, 211, 153))
        painter.drawText(right_rect, Qt.AlignCenter, "✓")

    # Center Box (Dead centered)
    center_rect = QRectF(x + 54, y, width - 108, height)
    painter.setFont(QFont("Segoe UI", 8, QFont.ExtraBold))
    painter.setPen(status_color)
    status_r = QRectF(center_rect.x(), center_rect.y() + 8, center_rect.width(), 16)
    painter.drawText(status_r, Qt.AlignCenter, status_text)

    painter.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
    painter.setPen(QColor(243, 244, 246))
    body_r = QRectF(center_rect.x(), center_rect.y() + 24, center_rect.width(), 20)
    painter.drawText(body_r, Qt.AlignCenter, body_text)


def create_hero_banner():
    b_w = 900
    b_h = 240
    pix = QPixmap(b_w, b_h)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    rect = QRectF(1, 1, b_w - 2, b_h - 2)
    path = QPainterPath()
    path.addRoundedRect(rect, 18.0, 18.0)

    # Ambient banner background
    banner_grad = QLinearGradient(0, 0, b_w, b_h)
    banner_grad.setColorAt(0.0, QColor(13, 17, 23))
    banner_grad.setColorAt(0.5, QColor(15, 23, 42))
    banner_grad.setColorAt(1.0, QColor(10, 14, 26))
    painter.fillPath(path, banner_grad)

    # Ambient Radial Glows
    glow1 = QRadialGradient(200, 40, 320)
    glow1.setColorAt(0.0, QColor(99, 102, 241, 55))
    glow1.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.fillRect(rect.toRect(), glow1)

    glow2 = QRadialGradient(720, 180, 260)
    glow2.setColorAt(0.0, QColor(244, 63, 94, 30))
    glow2.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.fillRect(rect.toRect(), glow2)

    # Border
    painter.setPen(QPen(QColor(255, 255, 255, 24), 1.2))
    painter.drawPath(path)

    # Title & Badges
    painter.setFont(QFont("Segoe UI Emoji", 24))
    painter.drawText(40, 68, "🎙️")

    painter.setFont(QFont("Segoe UI", 20, QFont.Bold))
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(82, 64, "Antigravity Global Voice Typing")

    # Hotkey pill tag
    hotkey_rect = QRectF(510, 42, 100, 24)
    hk_path = QPainterPath()
    hk_path.addRoundedRect(hotkey_rect, 6.0, 6.0)
    painter.fillPath(hk_path, QColor(239, 68, 68, 35))
    painter.setPen(QPen(QColor(239, 68, 68, 110), 1))
    painter.drawPath(hk_path)
    painter.setFont(QFont("Cascadia Code", 9, QFont.Bold))
    painter.setPen(QColor(248, 113, 113))
    painter.drawText(hotkey_rect, Qt.AlignCenter, "Alt + V")

    # Subtitle
    painter.setFont(QFont("Segoe UI", 11))
    painter.setPen(QColor(148, 163, 184))
    painter.drawText(42, 94, "Lightweight, system-wide AI speech dictation HUD for Windows with zero focus loss.")

    # Embedded Floating Pill Preview in Banner
    draw_pill(
        painter,
        x=(b_w - 580) / 2,
        y=134,
        width=580,
        height=58,
        icon="🎙️",
        status_text="LISTENING · PRESS ALT + V TO FINISH",
        status_color=QColor(248, 113, 113),
        body_text="Type with your voice into any application seamlessly...",
        right_type="waveform",
        wave_bars=[0.3, 0.8, 0.95, 0.65, 0.4]
    )

    painter.end()
    out_path = os.path.join(output_dir, "hero_banner.png")
    pix.save(out_path, "PNG")
    print("Generated asset: hero_banner.png")


def create_step_card(step_num, step_badge_color, step_title, step_desc, pill_props, filename):
    pix = QPixmap(W, H)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    card_rect = QRectF(1, 1, W - 2, H - 2)
    path = QPainterPath()
    path.addRoundedRect(card_rect, 16.0, 16.0)

    # Card background (Deep charcoal canvas with subtle mesh)
    card_grad = QLinearGradient(0, 0, 0, H)
    card_grad.setColorAt(0.0, QColor(13, 17, 23))
    card_grad.setColorAt(1.0, QColor(10, 13, 18))
    painter.fillPath(path, card_grad)

    # Card border
    border_pen = QPen(QColor(255, 255, 255, 22), 1.2)
    painter.setPen(border_pen)
    painter.drawPath(path)

    # Step Badge
    badge_rect = QRectF(32, 26, 74, 24)
    b_path = QPainterPath()
    b_path.addRoundedRect(badge_rect, 6.0, 6.0)
    painter.fillPath(b_path, QColor(step_badge_color.red(), step_badge_color.green(), step_badge_color.blue(), 30))
    painter.setPen(QPen(QColor(step_badge_color.red(), step_badge_color.green(), step_badge_color.blue(), 100), 1))
    painter.drawPath(b_path)

    painter.setFont(QFont("Cascadia Code", 9, QFont.Bold))
    painter.setPen(step_badge_color)
    painter.drawText(badge_rect, Qt.AlignCenter, f"STEP {step_num}")

    # Title
    painter.setFont(QFont("Segoe UI", 15, QFont.Bold))
    painter.setPen(QColor(240, 246, 252))
    painter.drawText(118, 44, step_title)

    # Description
    painter.setFont(QFont("Segoe UI", 10))
    painter.setPen(QColor(139, 148, 158))
    painter.drawText(34, 76, step_desc)

    # Divider line
    painter.setPen(QPen(QColor(255, 255, 255, 14), 1))
    painter.drawLine(32, 94, W - 32, 94)

    # Pill container area
    pill_w = pill_props.get("width", 560)
    pill_h = 58
    pill_x = (W - pill_w) / 2
    pill_y = 135

    # Decorative background simulator
    bg_box = QRectF(32, 108, W - 64, 126)
    bg_path = QPainterPath()
    bg_path.addRoundedRect(bg_box, 10.0, 10.0)
    painter.fillPath(bg_path, QColor(6, 8, 13, 160))
    painter.setPen(QPen(QColor(255, 255, 255, 10), 1))
    painter.drawPath(bg_path)

    # Draw the HUD pill
    draw_pill(
        painter,
        x=pill_x,
        y=pill_y,
        width=pill_w,
        height=pill_h,
        icon=pill_props["icon"],
        status_text=pill_props["status"],
        status_color=pill_props["status_color"],
        body_text=pill_props["body"],
        right_type=pill_props.get("right_type", "waveform"),
        wave_bars=pill_props.get("wave_bars")
    )

    painter.end()
    out_path = os.path.join(output_dir, filename)
    pix.save(out_path, "PNG")
    print(f"Generated asset: {filename}")


create_hero_banner()

# 1. Step 1: Trigger Hotkey
create_step_card(
    step_num="01",
    step_badge_color=QColor(56, 189, 248),
    step_title="Focus Any Text Field & Trigger with Alt + V",
    step_desc="Click into any editor, browser input, Discord, or Notepad. Press Alt + V to summon the HUD without losing typing cursor focus.",
    pill_props={
        "width": 540,
        "icon": "🎙️",
        "status": "LISTENING · PRESS ALT + V TO FINISH",
        "status_color": QColor(248, 113, 113),
        "body": "Speak now, transcribing in real-time...",
        "right_type": "waveform",
        "wave_bars": [0.15, 0.25, 0.2, 0.25, 0.15]
    },
    filename="step1_trigger.png"
)

# 2. Step 2: Listening & Waveform
create_step_card(
    step_num="02",
    step_badge_color=QColor(248, 113, 113),
    step_title="Instant Patterned HUD & Reactive Waveform",
    step_desc="The frameless glassmorphic pill floats at the top with a subtle micro-dot matrix pattern and live reacting audio frequency bars.",
    pill_props={
        "width": 550,
        "icon": "🎙️",
        "status": "LISTENING · AUDIO ENGINE ACTIVE",
        "status_color": QColor(248, 113, 113),
        "body": "Listening for speech... (16kHz 16-bit PCM)",
        "right_type": "waveform",
        "wave_bars": [0.4, 0.85, 0.95, 0.7, 0.35]
    },
    filename="step2_listening.png"
)

# 3. Step 3: Speaking & Streaming
create_step_card(
    step_num="03",
    step_badge_color=QColor(168, 85, 247),
    step_title="Real-Time Streaming Speech-to-Text",
    step_desc="Spoken words flow into the pill in real-time with zero cloud delay via the local Antigravity Language Server engine.",
    pill_props={
        "width": 580,
        "icon": "🎙️",
        "status": "LISTENING · STREAMING TRANSCRIPTION",
        "status_color": QColor(56, 189, 248),
        "body": "Antigravity global voice typing writes code anywhere with your voice...",
        "right_type": "waveform",
        "wave_bars": [0.55, 0.9, 0.75, 0.85, 0.6]
    },
    filename="step3_speaking.png"
)

# 4. Step 4: Text Inserted
create_step_card(
    step_num="04",
    step_badge_color=QColor(52, 211, 153),
    step_title="Automatic Text Injection & Dead-Center Confirmation",
    step_desc="Press Alt + V again to finish. The text is seamlessly injected into your active application with mathematical center alignment.",
    pill_props={
        "width": 570,
        "icon": "✍️",
        "status": "TEXT INSERTED",
        "status_color": QColor(52, 211, 153),
        "body": "Antigravity global voice typing writes code anywhere with your voice",
        "right_type": "badge"
    },
    filename="step4_inserted.png"
)

print("All step showcase graphics generated successfully!")
