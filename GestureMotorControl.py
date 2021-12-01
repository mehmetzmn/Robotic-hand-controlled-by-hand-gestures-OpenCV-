import cv2
import numpy as np
import HandTrackingModule as htm
import math
import pyfirmata

board = pyfirmata.Arduino("COM10")

iter8 = pyfirmata.util.Iterator(board)
iter8.start()

pin2 = board.get_pin('d:2:s')
pin4 = board.get_pin('d:4:s')
pin6 = board.get_pin('d:6:s')
pin8 = board.get_pin('d:8:s')
pin10 = board.get_pin('d:10:s')
pin12 = board.get_pin('d:12:s')

wCam, hCam = 640, 480

cap = cv2.VideoCapture(2)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.75)


def move_servo(a):
    if a == thumb_angle:
        pin2.write(a)
    elif a == index_angle:
        pin4.write(a)
    elif a == middle_angle:
        pin6.write(a)
    elif a == ring_angle:
        pin8.write(a)
    elif a == pinky_angle:
        pin10.write(a)
    elif a == wrist_turn_angle:
        pin12.write(a)


while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[1], lmList[17])

        thumb_x, thumb_y = lmList[4][1], lmList[4][2]
        index_x, index_y = lmList[8][1], lmList[8][2]
        middle_x, middle_y = lmList[12][1], lmList[12][2]
        ring_x, ring_y = lmList[16][1], lmList[16][2]
        pinky_x, pinky_y = lmList[20][1], lmList[20][2]
        wrist_x, wrist_y = lmList[0][1], lmList[0][2]

        cv2.circle(img, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (wrist_x, wrist_y), 10, (255, 0, 255), cv2.FILLED)
        # cv2.line(img, (index_x, index_y), (wrist_x, wrist_y), (255, 0, 255), 3)

        thumb_length = math.hypot(wrist_x - thumb_x, wrist_y - thumb_y)
        index_length = math.hypot(wrist_x - index_x, wrist_y - index_y)
        middle_length = math.hypot(wrist_x - middle_x, wrist_y - middle_y)
        ring_length = math.hypot(wrist_x - ring_x, wrist_y - ring_y)
        pinky_length = math.hypot(wrist_x - pinky_x, wrist_y - pinky_y)

        # Index finger range 330 - 140
        # servo motor angle range 180 - 0
        index_angle = np.interp(index_length, [140, 300], [0, 180])
        # Thumb finger range 250 - 120
        thumb_angle = np.interp(thumb_length, [120, 250], [0, 180])
        # Middle finger range 370 - 120
        middle_angle = np.interp(middle_length, [120, 370], [0, 180])
        # Ring finger range 350- 90
        ring_angle = np.interp(ring_length, [90, 350], [0, 180])
        # Pinky finger range 290 - 120
        pinky_angle = np.interp(pinky_length, [120, 290], [0, 180])
        # print(int(index_angle), int(pinky_angle))

        move_servo(thumb_angle)
        move_servo(index_angle)
        move_servo(middle_angle)
        move_servo(ring_angle)
        move_servo(pinky_angle)

        # Bilek kısmının döndürülmesi için 5 ve 17' nci landmark' a bakılır

        wrist_pnt1_x, wrist_pnt1_y = lmList[5][1], lmList[5][2]
        wrist_pnt2_x, wrist_pnt2_y = lmList[17][1], lmList[17][2]

        wrist_turn = math.hypot(wrist_pnt2_x - wrist_pnt1_x,
                                wrist_pnt2_y - wrist_pnt1_y)

        # print(int(wrist_turn))

        # wrist turn range 110 - 70
        wrist_turn_angle = np.interp(wrist_turn, [70, 110], [0, 90])

        # print(int(wrist_turn_angle))
        move_servo(wrist_turn_angle)
        print(f'başparmak: {int(thumb_angle)}, işaret parmağı: {int(index_angle)}, ortaparmak: {int(middle_angle)},' 
              f'yüzük parmağı: {int(ring_angle)}, serçe parmağı: {int(pinky_angle)}, bilek: {int(wrist_turn_angle)}')

    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key & 0xff == ord('q'):
        break
