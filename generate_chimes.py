import struct
import math
import os

def create_smooth_chime(file_path: str, tones: list, total_duration: float = 0.12, volume: float = 0.35):
    """
    tones: list of (freq, start_ratio, end_ratio)
    e.g. [(880, 0.0, 0.5), (1320, 0.45, 1.0)]
    """
    sample_rate = 44100
    num_samples = int(sample_rate * total_duration)
    pcm = bytearray()
    
    for i in range(num_samples):
        t = i / sample_rate
        ratio = i / num_samples
        
        # Calculate combined amplitude from active tones
        val = 0.0
        for freq, start_r, end_r in tones:
            if start_r <= ratio <= end_r:
                tone_len = (end_r - start_r) * total_duration
                tone_t = (ratio - start_r) * total_duration
                # Smooth cosine envelope
                tone_env = math.sin(math.pi * (tone_t / tone_len))
                val += math.sin(2.0 * math.pi * freq * t) * tone_env
                
        # Master fade-in/fade-out
        master_env = 1.0
        fade_samples = int(0.004 * sample_rate)
        if i < fade_samples:
            master_env = i / fade_samples
        elif i > num_samples - fade_samples:
            master_env = (num_samples - i) / fade_samples
            
        sample = int(32767.0 * volume * master_env * val)
        sample = max(-32768, min(32767, sample))
        pcm.extend(struct.pack('<h', sample))
        
    hdr = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + len(pcm),
        b'WAVE',
        b'fmt ',
        16, 1, 1,
        sample_rate, sample_rate * 2, 2, 16,
        b'data', len(pcm)
    )
    with open(file_path, 'wb') as f:
        f.write(hdr + pcm)

assets_dir = r"C:\Users\eGe\Vault\🏰 300-Projects\Antigravity-Voice-Typing\assets"
os.makedirs(assets_dir, exist_ok=True)

# 1. Start Chime: Elegant ascending chime (880 Hz to 1320 Hz, A5 to E6)
start_wav = os.path.join(assets_dir, "start.wav")
create_smooth_chime(
    start_wav,
    tones=[(880.0, 0.0, 0.6), (1320.0, 0.35, 1.0)],
    total_duration=0.14,
    volume=0.30
)

# 2. Stop Chime: Soft descending resolution chime (1175 Hz to 784 Hz, D6 to G5)
stop_wav = os.path.join(assets_dir, "stop.wav")
create_smooth_chime(
    stop_wav,
    tones=[(1174.66, 0.0, 0.55), (783.99, 0.35, 1.0)],
    total_duration=0.13,
    volume=0.28
)

print(f"Generated start.wav ({os.path.getsize(start_wav)} bytes)")
print(f"Generated stop.wav ({os.path.getsize(stop_wav)} bytes)")
