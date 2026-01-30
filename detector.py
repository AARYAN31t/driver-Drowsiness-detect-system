import cv2
import numpy as np
import time
import os

class DrowsinessDetector:
    def __init__(self, ear_threshold=0.30, time_threshold=60.0, mar_threshold=0.6):
        # Paths
        haarcascade_path = cv2.data.haarcascades
        face_path = os.path.join(haarcascade_path, 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(face_path)
        
        # Facemark LBF
        self.facemark = cv2.face.createFacemarkLBF()
        model_path = os.path.join(os.path.dirname(__file__), "lbfmodel.yaml")
        try:
            self.facemark.loadModel(model_path)
            self.has_facemark = True
        except Exception as e:
            print(f"Error loading Facemark model: {e}")
            self.has_facemark = False

        self.ear_threshold = ear_threshold
        self.mar_threshold = mar_threshold
        self.time_threshold = time_threshold
        
        self.drowsy = False
        self.eye_closed_start_time = None
        
        self.blink_count = 0
        self.yawn_count = 0
        self.eye_closed = False
        self.yawning = False
        self.consecutive_open_frames = 0
        
        # 68-point landmarks indices
        # Left Eye: 36-41 (0-based: 36,37,38,39,40,41)
        self.LEFT_EYE = list(range(36, 42))
        # Right Eye: 42-47
        self.RIGHT_EYE = list(range(42, 48))
        # Mouth: 48-67. Inner lips: 60-67. outer: 48-59
        # MAR usually uses 6 points from inner or outer. Let's use outer.
        # P1: 48, P2: 50, P3: 52, P4: 54, P5: 56, P6: 58 (Just an example, let's use standard MAR indices from 68pts)
        # Standard MAR:
        # A = dist(50, 58)
        # B = dist(52, 56)
        # C = dist(48, 54)
        # MAR = (A + B) / (2.0 * C)
        self.MOUTH = [48, 50, 52, 54, 56, 58]

    def calculate_ear(self, landmarks, indices):
        # indices: p1, p2, p3, p4, p5, p6
        # vertical 1: p2 - p6 (1, 5)
        # vertical 2: p3 - p5 (2, 4)
        # horizontal: p1 - p4 (0, 3)
        p = landmarks[indices]
        v1 = np.linalg.norm(p[1] - p[5])
        v2 = np.linalg.norm(p[2] - p[4])
        h = np.linalg.norm(p[0] - p[3])
        return (v1 + v2) / (2.0 * h)

    def calculate_mar(self, landmarks):
        # MOUTH indices mapped to 68-points:
        # 50(1), 58(5) -> v1
        # 52(2), 56(4) -> v2
        # 48(0), 54(3) -> h
        # My self.MOUTH is [48, 50, 52, 54, 56, 58]
        # p[0]=48, p[1]=50, p[2]=52, p[3]=54, p[4]=56, p[5]=58
        p = landmarks[self.MOUTH]
        v1 = np.linalg.norm(p[1] - p[5])
        v2 = np.linalg.norm(p[2] - p[4])
        h = np.linalg.norm(p[0] - p[3])
        return (v1 + v2) / (2.0 * h)

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        status = "Awake"
        ear = 0.0
        mar = 0.0
        
        if len(faces) > 0:
            if self.has_facemark:
                success, landmarks = self.facemark.fit(frame, faces)
                if success:
                    # Handle variable dimensions of landmarks
                    # landmarks is list of numpy arrays. landmarks[0] is for first face.
                    face_landmarks = landmarks[0]
                    if len(face_landmarks.shape) == 3:
                        shape = face_landmarks[0] # (1, 68, 2) -> (68, 2)
                    else:
                        shape = face_landmarks # (68, 2)
                    
                    left_ear = self.calculate_ear(shape, self.LEFT_EYE)
                    right_ear = self.calculate_ear(shape, self.RIGHT_EYE)
                    ear = (left_ear + right_ear) / 2.0
                    
                    mar = self.calculate_mar(shape)
                    
                    # Logic same as before
                    # Logic with Debounce for Robustness
                    if ear < self.ear_threshold:
                        self.consecutive_open_frames = 0 # Reset open counter
                        
                        if not self.eye_closed:
                            self.eye_closed = True
                            self.eye_closed_start_time = time.time()
                        else:
                            duration = time.time() - self.eye_closed_start_time
                            if duration >= self.time_threshold:
                                self.drowsy = True
                                status = "DROWSY!"
                    else:
                        self.consecutive_open_frames += 1
                        # Only consider eyes open if they stay open for > 3 frames
                        # This prevents single-frame detection noise from resetting the timer
                        if self.eye_closed and self.consecutive_open_frames > 2:
                            # Eye opened
                            duration = time.time() - self.eye_closed_start_time
                            if duration < self.time_threshold: 
                                self.blink_count += 1
                            self.eye_closed = False
                            self.eye_closed_start_time = None
                            self.drowsy = False

                    if mar > self.mar_threshold:
                        if not self.yawning:
                            self.yawn_count += 1
                            self.yawning = True
                    else:
                        self.yawning = False
                        
                    # Draw landmarks
                    for (x, y) in shape:
                         cv2.circle(frame, (int(x), int(y)), 1, (0, 255, 255), -1)

            else:
                # Fallback if facemark failed to load but face detected
                status = "Face Detect (No LM)"
                
            # Draw face box
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                break # only first face
                
            return status, None, ear, mar
            
        return "No Face", None, 0, 0
