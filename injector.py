"""
Text Injector
Kullanıcının o sırada seçili/odaklanmış olduğu herhangi bir Windows penceresine
(Notepad, Tarayıcı, Discord, Word, Terminal vb.) tanınan metni anında yapıştırır.
"""

import ctypes
import time
import win32clipboard
import win32con
from typing import Optional

user32 = ctypes.windll.user32

VK_CONTROL = 0x11
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002

class TextInjector:
    def __init__(self):
        pass

    def get_current_window(self) -> int:
        """Kullanıcının şu anda odaklanmış olduğu pencerenin HWND tutamacını alır."""
        return user32.GetForegroundWindow()

    def paste_text(self, text: str, target_hwnd: Optional[int] = None) -> bool:
        """
        Verilen metni panoya kopyalar, hedef pencereye odaklanır ve Ctrl+V basarak yapıştırır.
        Eski pano içeriğini yedekleyip kısa süre sonra geri yükler.
        """
        if not text:
            return False

        # 1. Eski pano içeriğini yedekle
        old_clipboard = None
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                old_clipboard = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception:
            pass

        # 2. Yeni metni panoya yaz
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"[Injector] Panoya yazma hatası: {e}")
            return False

        # 3. Hedef pencereye odaklan
        if target_hwnd:
            user32.SetForegroundWindow(target_hwnd)
            time.sleep(0.06)

        # 4. Ctrl + V simüle et
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_V, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

        # 5. Eski panoyu arka planda geri yükle (opsiyonel)
        def restore_clipboard():
            time.sleep(0.5)
            if old_clipboard is not None:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(old_clipboard, win32con.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass

        import threading
        threading.Thread(target=restore_clipboard, daemon=True).start()
        return True
