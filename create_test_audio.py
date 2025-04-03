import wave
import struct
import math

# Create a simple sine wave WAV file
sample_rate = 16000
duration = 3  # seconds
frequency = 1000  # Hz

with wave.open('test.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    
    for i in range(int(duration * sample_rate)):
        value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        data = struct.pack('<h', value)
        wav_file.writeframesraw(data)

print("Created test.wav successfully")