# save this as create_beep.py
import numpy as np
from scipy.io.wavfile import write

sample_rate = 44100  # Hz
duration = 1.0  # seconds
frequency = 440  # Hz (A4 musical note)

t = np.linspace(0, duration, int(sample_rate * duration), False)
audio = np.sin(2 * np.pi * frequency * t) * 0.3  # 30% volume
audio = np.int16(audio * 32767)  # Convert to 16-bit PCM

write("beep.wav", sample_rate, audio)
print("Created beep.wav")