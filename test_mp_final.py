import sys
print(f"Python: {sys.version}")
try:
    import mediapipe as mp
    print(f"MediaPipe file: {mp.__file__}")
    try:
        sol = mp.solutions.face_mesh
        print("Success: mp.solutions.face_mesh available")
        mesh = sol.FaceMesh()
        print("Success: FaceMesh instantiated")
    except Exception as e:
        print(f"Error accessing solutions: {e}")
except Exception as e:
    print(f"Error importing mediapipe: {e}")
