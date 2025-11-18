#LIBRARIES
import cv2
import mediapipe as mp
import math
from time import time
from pynput.keyboard import Controller, Key
from Button import Button 

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
W, H = 1280, 720
cap.set(3, W)
cap.set(4, H)

keyboard = Controller()

HOVER_COLOR = (0, 165, 255)
CLICK_COLOR = (0, 255, 0)   
TEXT_COLOR = (50, 50, 50)

KEY_WIDTH, KEY_HEIGHT = 85, 85
GAP = 15
PINCH_THRESHOLD = 45 

keys_letters = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M"]
]

keyboard_width = len(keys_letters[0]) * (KEY_WIDTH + GAP) - GAP
keyboard_height = len(keys_letters) * (KEY_HEIGHT + GAP) - GAP

start_x = int((W - keyboard_width) / 2)
start_y = int((H - keyboard_height) / 2) 

buttonList = []

for i in range(len(keys_letters)):
    for j, key in enumerate(keys_letters[i]):
        x_pos = start_x + j * (KEY_WIDTH + GAP)
        y_pos = start_y + i * (KEY_HEIGHT + GAP)
        buttonList.append({
            "obj": Button([x_pos, y_pos], key, size=[KEY_WIDTH, KEY_HEIGHT]),
            "action": key
        })

last_row_width = len(keys_letters[-1]) * (KEY_WIDTH + GAP) - GAP
x_pos_del = start_x + last_row_width + 40
y_pos_del = start_y + 2 * (KEY_HEIGHT + GAP) 

buttonList.append({
    "obj": Button([x_pos_del, y_pos_del], "Sil", size=[150, KEY_HEIGHT]),
    "action": Key.backspace
})

smooth_x8, smooth_y8 = 0, 0
alpha = 0.7 

last_click_time = 0
COOLDOWN_TIME = 0.35 

def main():
    global last_click_time, smooth_x8, smooth_y8

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        imgNew = img.copy()

        for bt in buttonList:
            bt["obj"].draw(imgNew)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * W), int(lm.y * H)
                    lmList.append([id, cx, cy])

                if lmList:
                    x8_raw, y8_raw = lmList[8][1], lmList[8][2]
                    x4, y4 = lmList[4][1], lmList[4][2]

                    if smooth_x8 == 0: 
                        smooth_x8, smooth_y8 = x8_raw, y8_raw
                    else:
                        smooth_x8 = int(smooth_x8 * alpha + x8_raw * (1 - alpha))
                        smooth_y8 = int(smooth_y8 * alpha + y8_raw * (1 - alpha))

                    x8, y8 = smooth_x8, smooth_y8

                    cv2.circle(imgNew, (x8, y8), 15, HOVER_COLOR, cv2.FILLED)
                    
                    distance = math.hypot(x8 - x4, y8 - y4)

                    for bt in buttonList:
                        button = bt["obj"]
                        x, y = button.pos
                        w, h = button.size
                        action = bt["action"]

                        if x < x8 < x + w and y < y8 < y + h:
                            cv2.rectangle(imgNew, (x - 3, y - 3), (x + w + 3, y + h + 3),
                                          HOVER_COLOR, cv2.FILLED)
                            cv2.putText(imgNew, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, TEXT_COLOR, 4)

                            if distance < PINCH_THRESHOLD and time() > last_click_time + COOLDOWN_TIME:
                                cv2.rectangle(imgNew, (x, y), (x + w, y + h),
                                              CLICK_COLOR, cv2.FILLED)
                                cv2.putText(imgNew, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, TEXT_COLOR, 4)

                                keyboard.press(action)
                                keyboard.release(action)

                                last_click_time = time()

        cv2.addWeighted(imgNew, 0.5, img, 0.5, 0, img)

        cv2.imshow("AirType CV - Sanal Klavye", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()