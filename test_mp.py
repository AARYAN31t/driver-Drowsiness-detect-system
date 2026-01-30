import sys
import cv2
print(f"Python: {sys.version}")
print(f"OpenCV: {cv2.__version__}")

try:
    if hasattr(cv2, 'face'):
        print("OpenCV Face module: Available")
    else:
        print("OpenCV Face module: Not Available")
except Exception as e:
    print(f"Error checking cv2.face: {e}")

try:
    import mediapipe as mp
    print(f"MediaPipe file: {mp.__file__}")
    print(f"Solutions: {mp.solutions}")
    print("MediaPipe Success!")
except Exception as e:
    print(f"MediaPipe Error: {e}")
