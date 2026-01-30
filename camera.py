import cv2

class Camera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None
        return frame
