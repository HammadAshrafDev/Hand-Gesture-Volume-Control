import cv2
import time
import numpy as np
from hand_volume import HandVolumeController

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # Width
    cap.set(4, 720)   # Height
    
    detector = HandVolumeController()
    
    # FPS calculation
    p_time = 0
    c_time = 0
    
    # Mute status
    is_muted = False
    mute_cooldown = 0
    
    while True:
        success, img = cap.read()
        if not success:
            continue
        
        img = cv2.flip(img, 1)  # Mirror the image
        img = detector.find_hands(img)
        lm_list = detector.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            # Thumb (4) and Index finger (8) tips
            thumb = lm_list[4]
            index = lm_list[8]
            
            # Get distance between thumb and index
            distance = detector.get_distance(thumb, index, img)
            
            # Volume control
            img = detector.volume_control(img, distance)
            
            # Check for mute gesture (pinch and hold)
            current_time = time.time()
            gesture = detector.check_gesture(distance, current_time)
            
            if gesture == "mute_toggle" and mute_cooldown < current_time:
                is_muted = detector.toggle_mute()
                mute_cooldown = current_time + 1  # 1 second cooldown
        
        # Display mute status
        if is_muted:
            cv2.putText(img, "MUTED", (400, 100),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
        
        # Calculate FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time
        cv2.putText(img, f'FPS: {int(fps)}', (10, 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        # Instructions
        cv2.putText(img, "Volume Control: Move thumb and index finger", (10, 650),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        cv2.putText(img, "Mute: Pinch and hold for 1 second", (10, 680),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        
        cv2.imshow("Volume Control", img)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()