# Driver Drowsiness Detection System

A full-stack AI web application that detects driver drowsiness using a webcam and alerts the user with an alarm and visual warnings.

## Features
- **Real-time Eye Tracking**: Uses MediaPipe Face Mesh for precise eye landmark detection.
- **Drowsiness Detection**: Calculates Eye Aspect Ratio (EAR) to detect closed eyes.
- **Audio & Visual Alerts**: Triggers a loud alarm and flashing UI when drowsiness is detected.
- **Dashboard**: React-based dashboard with live video feed and status updates.

## Tech Stack
- **Backend**: Python, Flask, OpenCV, MediaPipe, Pygame
- **Frontend**: React, Vite
- **Communication**: HTTP (Axios) + MJPEG Stream

## Setup & Running

### Prerequisites
- Python 3.8+
- Node.js & npm

### 1. Backend Setup
Recommended to use a virtual environment to avoid conflicts.
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python generate_sound.py
python app.py
```
The backend will run on `http://localhost:5000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will run on `http://localhost:5173`.

## Usage
1. Open the frontend URL in your browser.
2. Allow camera access.
3. The dashboard will show your status ("Awake" or "Drowsy").
4. Close your eyes for >2 seconds to trigger the alarm.
