"""
Antigravity Voice Bridge
Connects to local Antigravity Language Server audio transcription endpoints.
Service: exa.language_server_pb.LanguageServerService
Methods:
  - StreamAudioTranscription (ConnectRPC streaming)
  - SendAudioChunk (ConnectRPC unary)
  - EndAudioSession (ConnectRPC unary)
"""

import psutil
import re
import ssl
import json
import struct
import urllib.request
import base64
import time
import threading
from typing import Callable, Optional, Tuple

class AntigravityBridge:
    def __init__(self):
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

        self.port: Optional[int] = None
        self.csrf_token: Optional[str] = None
        self.last_discovery_time = 0

        self.active_session_id: Optional[str] = None
        self.stream_resp = None
        self.stream_running = False
        self.reader_thread: Optional[threading.Thread] = None
        self.sequence_number = 0

    def discover(self, force=False) -> Tuple[Optional[int], Optional[str]]:
        """Dynamically finds the local language_server.exe process, listening port, and CSRF token."""
        now = time.time()
        if not force and self.port and self.csrf_token and (now - self.last_discovery_time < 30):
            if self._verify_port(self.port, self.csrf_token):
                return self.port, self.csrf_token

        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = p.info.get('name') or ''
                if 'language_server' in name.lower():
                    cmd = ' '.join(p.info.get('cmdline') or [])
                    csrf_m = re.search(r'--csrf_token[=\s]+([^\s]+)', cmd)
                    if not csrf_m:
                        continue
                    csrf = csrf_m.group(1)

                    ports = []
                    for conn in p.net_connections(kind='tcp'):
                        if conn.status == psutil.CONN_LISTEN and conn.laddr.ip in ('127.0.0.1', '0.0.0.0'):
                            ports.append(conn.laddr.port)

                    for port in ports:
                        if self._verify_port(port, csrf):
                            self.port = port
                            self.csrf_token = csrf
                            self.last_discovery_time = now
                            return port, csrf
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return None, None

    def _verify_port(self, port: int, csrf: str) -> bool:
        try:
            req = urllib.request.Request(
                f'https://127.0.0.1:{port}/',
                headers={'x-codeium-csrf-token': csrf}
            )
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=0.4) as resp:
                return resp.status == 200
        except Exception:
            return False

    def is_available(self) -> bool:
        port, csrf = self.discover()
        return bool(port and csrf)

    def start_session(
        self,
        on_transcription: Callable[[str, bool], None],
        on_ready: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> bool:
        """Starts a new voice transcription session and opens the ConnectRPC stream."""
        port, csrf = self.discover(force=True)
        if not port or not csrf:
            if on_error:
                on_error(RuntimeError("Antigravity Language Server not detected! Please ensure Antigravity is running."))
            return False

        try:
            req_body = json.dumps({
                "mimeType": "audio/pcm;rate=16000",
                "preCursorText": "",
                "postCursorText": "",
                "cascadeId": "",
                "continuous": False
            }).encode('utf-8')

            # Connect-Protocol 5-byte envelope: [flag=0, length (4 bytes uint32 BE)]
            envelope = struct.pack('>BI', 0, len(req_body)) + req_body

            stream_req = urllib.request.Request(
                f'https://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/StreamAudioTranscription',
                data=envelope,
                headers={
                    'Content-Type': 'application/connect+json',
                    'x-codeium-csrf-token': csrf,
                    'Connect-Protocol-Version': '1'
                }
            )

            self.stream_resp = urllib.request.urlopen(stream_req, context=self.ssl_ctx)

            # Read first envelope message (AudioStreamReady -> sessionId)
            header = self.stream_resp.read(5)
            if len(header) < 5:
                raise RuntimeError("Failed to read ConnectRPC header")

            flag, length = struct.unpack('>BI', header)
            first_msg = json.loads(self.stream_resp.read(length).decode('utf-8'))
            ready_info = first_msg.get('ready', {})
            session_id = ready_info.get('sessionId')

            if not session_id:
                raise RuntimeError(f"Session ID missing in response: {first_msg}")

            self.active_session_id = session_id
            self.sequence_number = 0
            self.stream_running = True

            if on_ready:
                on_ready(session_id)

            # Background stream reader
            def reader_loop():
                try:
                    while self.stream_running:
                        h = self.stream_resp.read(5)
                        if not h or len(h) < 5:
                            break
                        f, l = struct.unpack('>BI', h)
                        payload = self.stream_resp.read(l)
                        if f == 0:
                            msg = json.loads(payload.decode('utf-8'))
                            if 'transcription' in msg:
                                t_info = msg['transcription']
                                text = t_info.get('text', '')
                                is_final = t_info.get('isFinal', False)
                                on_transcription(text, is_final)
                            elif 'complete' in msg:
                                if on_complete:
                                    on_complete()
                        elif f == 2:
                            # End of stream envelope
                            break
                except Exception as e:
                    if self.stream_running and on_error:
                        on_error(e)
                finally:
                    self.stream_running = False

            self.reader_thread = threading.Thread(target=reader_loop, daemon=True)
            self.reader_thread.start()
            return True

        except Exception as e:
            if on_error:
                on_error(e)
            return False

    def send_audio_chunk(self, pcm16_bytes: bytes) -> bool:
        """Sends a 16000Hz 16-bit PCM audio chunk to the server."""
        if not self.stream_running or not self.active_session_id:
            return False

        port = self.port
        csrf = self.csrf_token
        session_id = self.active_session_id
        seq = self.sequence_number
        self.sequence_number += 1

        b64_data = base64.b64encode(pcm16_bytes).decode('ascii')
        chunk_body = json.dumps({
            "sessionId": session_id,
            "data": b64_data,
            "sequenceNumber": seq
        }).encode('utf-8')

        chunk_req = urllib.request.Request(
            f'https://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/SendAudioChunk',
            data=chunk_body,
            headers={
                'Content-Type': 'application/json',
                'x-codeium-csrf-token': csrf,
                'Connect-Protocol-Version': '1'
            }
        )

        try:
            with urllib.request.urlopen(chunk_req, context=self.ssl_ctx, timeout=0.8) as resp:
                return resp.status == 200
        except Exception:
            return False

    def end_session(self) -> bool:
        """Ends the audio session and yields final transcription."""
        if not self.active_session_id:
            return False

        port = self.port
        csrf = self.csrf_token
        session_id = self.active_session_id

        end_body = json.dumps({"sessionId": session_id}).encode('utf-8')
        end_req = urllib.request.Request(
            f'https://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/EndAudioSession',
            data=end_body,
            headers={
                'Content-Type': 'application/json',
                'x-codeium-csrf-token': csrf,
                'Connect-Protocol-Version': '1'
            }
        )

        try:
            with urllib.request.urlopen(end_req, context=self.ssl_ctx, timeout=1.5) as resp:
                success = (resp.status == 200)
        except Exception:
            success = False

        self.active_session_id = None
        return success
