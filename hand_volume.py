import cv2
import mediapipe as mp
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class HandVolumeController:
    def __init__(self):
        # MediaPipe hands setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Volume control setup
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Volume range (pycaw gives -65.25 to 0)
        self.vol_range = self.volume.GetVolumeRange()
        self.min_vol, self.max_vol = self.vol_range[0], self.vol_range[1]
        
        # Variables for smoothing
        self.vol = 0
        self.vol_bar = 400
        self.vol_per = 0
        self.smoothness = 10
        self.vol_history = []
        
        # Gesture control
        self.gesture_threshold = 50
        self.pinched = False
        self.last_gesture_time = 0
        self.gesture_hold_time = 1  # seconds
        
    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img
    
    def find_position(self, img, hand_no=0, draw=True):
        lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        
        return lm_list
    
    def get_distance(self, p1, p2, img=None, draw=True):
        x1, y1 = p1[1], p1[2]
        x2, y2 = p2[1], p2[2]
        length = np.hypot(x2 - x1, y2 - y1)
        
        if img is not None and draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(length)}', (x1 + 20, y1 - 30),
                       cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        return length
    
    def volume_control(self, img, distance, draw=True):
        # Convert distance to volume level (distance range 30-250)
        vol = np.interp(distance, [30, 250], [self.min_vol, self.max_vol])
        
        # Smooth volume changes
        self.vol_history.append(vol)
        if len(self.vol_history) > self.smoothness:
            self.vol_history.pop(0)
        
        self.vol = int(sum(self.vol_history) / len(self.vol_history))
        self.volume.SetMasterVolumeLevel(self.vol, None)
        
        # Convert volume to percentage and bar length
        self.vol_per = np.interp(self.vol, [self.min_vol, self.max_vol], [0, 100])
        self.vol_bar = np.interp(self.vol, [self.min_vol, self.max_vol], [400, 150])
        
        if draw:
            # Volume bar
            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(self.vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(self.vol_per)}%', (40, 450),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            
            # Current volume level
            cv2.putText(img, f'Vol: {int(self.vol_per)}%', (400, 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        return img
    
    def check_gesture(self, distance, current_time):
        if distance < self.gesture_threshold:
            if not self.pinched:
                self.pinched = True
                self.last_gesture_time = current_time
            elif current_time - self.last_gesture_time > self.gesture_hold_time:
                return "mute_toggle"
        else:
            self.pinched = False
        
        return None
    
    def toggle_mute(self):
        is_muted = self.volume.GetMute()
        self.volume.SetMute(not is_muted, None)
        return not is_muted