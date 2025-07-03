# Volume Control with Hand Gestures using OpenCV and MediaPipe by HammadAshrafDev

A fun and practical computer vision project to control your system volume by simply moving your thumb and index finger closer or farther apart using your webcam. Lightweight and reuseable modules for your personal projects.

---

## 🧠 Tech Stack

- **OpenCV** – Webcam capture and visual feedback
- **MediaPipe** – Real-time hand tracking
- **pycaw** – Windows audio control
- **NumPy** – Math and distance calculations
- **Custom UI** – Visual volume bar and gesture indicators

---

## 📁 Project Structure

volume_control/

│── volume_controller.py # Main application

│── hand_volume.py # Hand tracking and volume logic

│── requirements.txt # Python dependencies


### 2. Install dependencies

```bash
pip install -r requirements.txt
```
# Usage
```bash
python volume_controller.py
```


# How It Works

The webcam captures your hand.

MediaPipe detects hand landmarks.

Distance between thumb and index finger is calculated.

Volume is adjusted using pycaw based on that distance.

UI overlays provide feedback including volume bar, mute indicator, and FPS counter.
