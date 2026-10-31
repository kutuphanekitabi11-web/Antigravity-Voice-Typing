# Antigravity Global Voice Typing 🎙️

Bu proje, bilgisayarınızda açık olan **Google Antigravity** masaüstü uygulamasının prompt girdi alanındaki mikrofon (ses kaydı / dikte) özelliğinin **tersine mühendislik (Reverse Engineering)** ile çözümlenmesi ve tüm Windows işletim sisteminde `Alt + V` kısayoluyla çalışacak şekilde sistem geneline uyarlanmış halidir.

---

## 🔍 Tersine Mühendislik (Reverse Engineering) Bulguları

REA (Reverse Engineer Anything) ve CDP (Chrome DevTools Protocol) araçları kullanılarak Antigravity uygulamasının ses mimarisi adım adım çözümlendi:

1. **Arka Plan Servisi (`language_server.exe`)**:
   - Antigravity IDE, arka planda `C:\Users\eGe\AppData\Local\Programs\Antigravity\resources\bin\language_server.exe` servisini çalıştırır.
   - Bu servis, dinamik bir yerel HTTPS portunda (`127.0.0.1:<port>`) bir **ConnectRPC** gRPC-web/HTTP sunucusu barındırır.
   - Yetkilendirme için Electron başlatılırken üretilen `--csrf_token` kullanılır (`x-codeium-csrf-token` HTTP başlığı).

2. **Protobuf & RPC Sözleşmesi (`language_server.proto`)**:
   - **Paket / Servis**: `exa.language_server_pb.LanguageServerService`
   - **Metotlar**:
     - `StreamAudioTranscription(StartAudioTranscriptionRequest) returns (stream StreamAudioTranscriptionResponse)`
       - ConnectRPC 5-byte envelope protokolü (`[0, len >> 24, ...]`) ile JSON mesaj akışı.
       - Parametreler: `mimeType: "audio/pcm;rate=16000"`, `continuous: false`.
       - Sunucu ilk mesajda `{"ready": {"sessionId": "..."}}` döndürür.
       - Ardından gerçek zamanlı `{"transcription": {"text": "...", "isFinal": false/true}}` akışı sağlar.
     - `SendAudioChunk(SendAudioChunkRequest) returns (SendAudioChunkResponse)`
       - 16000Hz 16-bit Mono PCM ses dilimlerini base64 olarak sunucuya yollar (`sessionId`, `data`, `sequenceNumber`).
     - `EndAudioSession(EndAudioSessionRequest) returns (EndAudioSessionResponse)`
       - Konuşma bittiğinde oturumu sonlandırır ve nihai transkripsiyonu üretir.

3. **Audio İşleme**:
   - Mikrofon akışı 16000 Hz, 1 kanal, 16-bit signed PCM olarak 40ms'lik dilimler (640 örnek) halinde paketlenir.

---

## 🚀 Nasıl Çalışır?

1. **Her Yerde Çalışır**: Notepad, Word, Chrome, WhatsApp, Discord, Terminal, VS Code, Obsidian veya herhangi bir metin kutusuna tıklayın.
2. **Kısayol (`Alt + V`)**:
   - `Alt + V` tuşuna basın: Ekranın alt kısmında modern, yarı saydam bir dikte hapı belirir ve mikrofon dinlemeye başlar.
   - Konuşun: Konuştuğunuz kelimeler gerçek zamanlı olarak arayüzde akar.
   - Tekrar `Alt + V` tuşuna basın (veya susun): Kayıt tamamlanır, metin otomatik olarak imlecin bulunduğu yere **yapıştırılır**.
3. **Sıfır Odak Kaybı**: Arayüz Windows üzerinde odağı (`focus`) asla çalmaz (`Qt.WindowDoesNotAcceptFocus`), böylece imleciniz hangi uygulamada ise tam oraya yazılır.

---

## 🛠️ Kurulum ve Başlatma

### Gereksinimler:
- Python 3.10+
- Gerekli Python kütüphaneleri (otomatik yüklenmiştir):
  ```bash
  pip install sounddevice numpy PyQt5 psutil pywin32
  ```

### Başlatma:
- **Arka Planda Çalıştırma**: Proje klasöründeki `baslat.bat` dosyasına çift tıklayın. Görev çubuğunda (System Tray) mikrofon simgesi görünecektir.
- **Konsollu (Hata Ayıklama) Çalıştırma**: `baslat_debug.bat` dosyasına çift tıklayın.

### Windows ile Otomatik Başlatma (İsteğe Bağlı):
1. `Win + R` tuşlarına basıp `shell:startup` yazın ve Enter'a basın.
2. `baslat.bat` dosyasının kısayolunu buraya kopyalayın. Bilgisayar her açıldığında otomatik olarak arka planda hazır olacaktır.
