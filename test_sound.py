import pygame
import os
import time

try:
    pygame.mixer.init()
    print("Mixer initialized")
    path = "backend/alarm.wav"
    if os.path.exists(path):
        print(f"File exists: {path}")
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        print("Playing...")
        time.sleep(3)
        pygame.mixer.music.stop()
        print("Stopped")
    else:
        print("File not found")
except Exception as e:
    print(f"Error: {e}")
