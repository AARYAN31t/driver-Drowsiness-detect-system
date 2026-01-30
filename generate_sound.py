import wave
import math
import struct
import os

def generate_alarm(filename="backend/alarm.wav", duration=1.0, frequency=440.0):
    if not os.path.exists("backend"):
        os.makedirs("backend")
        
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    amplitude = 16000
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

if __name__ == "__main__":
    generate_alarm()
    print(f"Created {os.path.abspath('backend/alarm.wav')}")
