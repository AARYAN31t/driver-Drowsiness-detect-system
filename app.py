from flask import Flask, Response, jsonify
from flask_cors import CORS
from camera import Camera
from detector import DrowsinessDetector
import cv2
import threading
import pygame
import os
import time

app = Flask(__name__)
CORS(app)

camera = None
try:
    # Set time_threshold to 60.0 seconds
    detector = DrowsinessDetector(ear_threshold=0.25, time_threshold=60.0) 
except Exception as e:
    print(f"Failed to initialize detector: {e}")
    detector = None

alarm_on = False
stop_thread = False
detection_active = False  # Global active state


volume = 1.0 # Default 100%

try:
    pygame.mixer.init()
except Exception as e:
    print(f"Audio init failed: {e}")

ALARM_PATH = os.path.join(os.path.dirname(__file__), "alarm.wav")

def play_alarm():
    global alarm_on, volume
    while alarm_on and not stop_thread:
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.load(ALARM_PATH)
                pygame.mixer.music.play()
                print(f"Playing alarm at vol {volume}")
            except Exception as e:
                print(f"Error playing alarm: {e}")
        time.sleep(0.1)


def generate_frames():
    global camera, alarm_on, detector, detection_active
    if camera is None:
        camera = Camera()
        
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
            
        if detection_active and detector:
            try:
                status, landmarks, ear, mar = detector.process_frame(frame)
                
                # Logic for alarm
                if status == "DROWSY!":
                    if not alarm_on:
                        alarm_on = True
                        threading.Thread(target=play_alarm, daemon=True).start()
                else:
                    alarm_on = False
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.stop()
                    except:
                        pass
            except Exception as e:
                print(f"Detection Error: {e}")
                status = "Error"
                ear, mar = 0, 0
                detection_active = False # Disable to allow recovery
        else:
            # If not active, just return frame with PAUSED text
            status, landmarks, ear, mar = "Paused", None, 0, 0
            if alarm_on: # Ensure alarm off if paused
                 alarm_on = False
                 try: pygame.mixer.music.stop() 
                 except: pass

        # Draw UI
        if detection_active:
             color = (0, 0, 255) if status == "DROWSY!" else (0, 255, 0)
             cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
             cv2.putText(frame, f"EAR: {ear:.2f} | Blinks: {detector.blink_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
             cv2.putText(frame, f"MAR: {mar:.2f} | Yawns: {detector.yawn_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
             cv2.putText(frame, "MONITORING PAUSED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
             cv2.putText(frame, "Press Start to Resume", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    global detection_active
    status = "Paused"
    blink = 0
    yawn = 0
    
    if detector:
        blink = detector.blink_count
        yawn = detector.yawn_count
        if detection_active:
            status = "Drowsy" if detector.drowsy else "Awake"
    
    return jsonify({
        "status": status,
        "active": detection_active,
        "blink_count": blink,
        "yawn_count": yawn
    })

@app.route('/start-detection', methods=['POST'])
def start_detection():
    global detection_active
    detection_active = True
    if detector:
        # Optional: detector.reset() if you want to clear counts on every start
        pass 
    return jsonify({"message": "Detection started", "active": True})

@app.route('/stop-detection', methods=['POST'])
def stop_detection():
    global detection_active
    detection_active = False
    return jsonify({"message": "Detection stopped", "active": False})

@app.route('/get-settings')
def get_settings():
    if detector:
        return jsonify({
            "threshold": detector.time_threshold,
            "volume": int(volume * 100)
        })
    return jsonify({"threshold": 60, "volume": 100})

@app.route('/set-settings', methods=['POST'])
def set_settings():
    global volume
    from flask import request
    data = request.json
    
    if detector:
        if 'threshold' in data:
            detector.time_threshold = float(data['threshold'])
            print(f"Updated threshold to: {detector.time_threshold}")
            
    if 'volume' in data:
        vol = float(data['volume'])
        volume = max(0.0, min(1.0, vol / 100.0))
        pygame.mixer.music.set_volume(volume)
        print(f"Updated volume to: {volume}")
        
    return jsonify({"message": "Settings updated", "volume": int(volume*100), "threshold": detector.time_threshold if detector else 60})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
