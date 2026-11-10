from pathlib import Path
import math, wave, random
import numpy as np

OUT = Path("outputs/audio")
OUT.mkdir(parents=True, exist_ok=True)

def generate_sound(description, index):
    # Efecto ambiental sintético local: mezcla de ruido filtrado y tonos suaves.
    sr, duration = 22050, 5.0
    n = int(sr * duration)
    rng = np.random.default_rng(index + 2026)
    noise = rng.normal(0, 1, n)
    # Suavizado simple para crear un ambiente menos áspero.
    kernel = np.ones(180) / 180
    ambience = np.convolve(noise, kernel, mode="same")
    t = np.arange(n) / sr
    tone = 0.10*np.sin(2*np.pi*(110 + 15*np.sin(2*np.pi*0.15*t))*t)
    envelope = np.minimum(1, t/0.7) * np.minimum(1, (duration-t)/0.8)
    audio = (0.42*ambience + tone) * envelope
    peak = max(1e-6, np.max(np.abs(audio)))
    pcm = (audio / peak * 0.65 * 32767).astype(np.int16)
    path = OUT / f"ambience_{index+1}.wav"
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())
    return path
