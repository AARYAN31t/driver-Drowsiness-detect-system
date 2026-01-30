import cv2
import sys
import os

print(f"OpenCV: {cv2.__version__}")
try:
    facemark = cv2.face.createFacemarkLBF()
    model_path = "backend/lbfmodel.yaml"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        # Try local dir
        model_path = "lbfmodel.yaml"
    
    facemark.loadModel(model_path)
    print("Success: Facemark LBF loaded!")
except Exception as e:
    print(f"Error loading Facemark: {e}")
