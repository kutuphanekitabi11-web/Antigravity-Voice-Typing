# Antigravity Global Voice Typing 🎙️

A lightweight, system-wide AI voice dictation HUD utility for Windows. Dictate text with your voice anywhere on your computer using a global hotkey (`Alt + V` or `Ctrl + Shift + V`).

Whether you are writing code in **VS Code**, taking notes in **Obsidian**, drafting emails in **Chrome**, chatting in **Discord**, or typing in **Word** and **Notepad**, simply press the hotkey, speak naturally, and your speech is converted to text and automatically pasted into your active input cursor.

---

## ✨ Features

- 🌍 **Universal Dictation Anywhere**: Works across all Windows applications. If you can click and type there, you can dictate there.
- ⚡ **Dual Intelligence Engine (Hybrid Architecture)**:
  - **Antigravity Engine**: Directly communicates with the local Antigravity Language Server engine for ultra-fast, accurate real-time speech transcription with zero cloud latency.
  - **Universal Fallback Engine**: Seamlessly falls back to universal speech recognition (Google Web Speech API) when Antigravity is not active or on machines without Antigravity installed. Works out of the box with zero setup.
- 💎 **Patterned Glassmorphic Floating HUD**:
  - A modern, frameless floating pill overlay at the top of your screen with micro-dot grid texturing and ambient glowing mesh styling.
  - Symmetrical 3-column layout guaranteeing 100% dead-center alignment for status cues and transcribed text.
  - Live animated waveform visualizer reacting in real time to your voice volume.
- 🎯 **Zero Focus Loss**:
  - Configured with `Qt.WindowDoesNotAcceptFocus` and native Win32 window management.
  - The floating overlay never steals focus from your active text field, keeping your typing cursor right where you left it.
- 🎹 **Multi-Tier Global Hotkey System**:
  - Global `Alt + V` (and alternate `Ctrl + Shift + V`) powered by native Win32 `RegisterHotKey` with low-level keyboard hook fallbacks.
  - Audio chimes provide subtle auditory confirmation when dictation starts and when text is inserted.
- 🖥️ **System Tray Integration**:
  - Lives quietly in your Windows system tray.
  - Displays engine connection status and enables one-click voice typing toggling directly from the tray icon.

---

## 🚀 How It Works

1. **Focus Any Text Field**: Click into any text field (browser address bar, code editor, chat box, terminal, document, etc.).
2. **Press `Alt + V`**:
   - The sleek floating HUD pill appears at the top of your screen.
   - The microphone activates with a soft audio cue and the live waveform animates to your speech.
3. **Speak Naturally**:
   - Your speech is transcribed in real-time as you talk.
4. **Press `Alt + V` Again (or pause)**:
   - Dictation finalizes, the overlay displays a centered confirmation badge, and the text is immediately pasted into your active cursor position.

---

## 📦 Installation & Setup

### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- Python 3.10+ installed

### 1. Clone the Repository
```bash
git clone https://github.com/kutuphanekitabi11-web/Antigravity-Voice-Typing.git
cd Antigravity-Voice-Typing
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

*Required packages: `sounddevice`, `numpy`, `PyQt5`, `psutil`, `pywin32`, `SpeechRecognition`, `keyboard`, `pynput`.*

---

## 🏃 Launching the Application

- **Background Silent Mode**: Double-click `baslat.bat`. The app starts silently with a tray icon in your taskbar.
- **Console / Debug Mode**: Double-click `baslat_debug.bat` to see live engine logs and recognition diagnostics in a terminal.

### Start Automatically with Windows (Optional)
1. Press `Win + R`, type `shell:startup`, and press `Enter`.
2. Right-click `baslat.bat` inside the project folder, select **Create shortcut**, and paste the shortcut into the Startup folder.
3. Antigravity Voice Typing will now be ready in the background whenever your PC boots up.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| `Alt + V` | Primary toggle: Start recording / Stop recording & paste |
| `Ctrl + Shift + V` | Secondary hotkey alternative |
| Left-Click Tray Icon | Start / Stop dictation toggle |

---

## 🏗️ Project Architecture

```
Antigravity-Voice-Typing/
├── app.py                 # Core application controller & system tray management
├── overlay_widget.py      # Patterned glassmorphic HUD pill with audio visualizer
├── antigravity_bridge.py  # Local streaming speech engine client (ConnectRPC)
├── fallback_engine.py     # Universal speech recognition engine
├── audio_engine.py        # 16kHz 16-bit Mono PCM audio capture & RMS level analyzer
├── injector.py            # Win32 foreground window preservation & text injection
├── hotkey_service.py      # Global hotkey listeners (RegisterHotKey + keyboard hooks)
├── baslat.bat             # Silent background Windows launcher
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

---

## 📄 License

MIT License. Free and open source for everyone.
