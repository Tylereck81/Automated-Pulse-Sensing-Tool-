import cv2
import mediapipe as mp
import time
from slope import getValue, find_m, getValueWithM
from math import dist
cap = cv2.VideoCapture('res/hand_1.mov')
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils
handLmsStyle = mpDraw.DrawingSpec(color=(150, 0, 150), thickness=3)
handConStyle = mpDraw.DrawingSpec(color=(200, 200, 0), thickness=5)
preTargetStyle = (0, 0, 255)
TargetStyle = (0, 255, 0)
pTime = 0
cTime = 0
infinity = 100000 # 以圖片像素來說等於無窮
while True:
    ret, img = cap.read()
    if ret:
        print("--------------------------")
        
        result = hands.process(img)
        
        imgHeight = img.shape[0]
        imgWidth = img.shape[1]
        total = 0.0
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#二值化
        ret, img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks: 
                originx = 0 #腕關節
                originy = 0
                bigFinger4_X = 0 #大拇指點4
                bigFinger4_Y = 0
                bigFinger3_X = 0 #大拇指點3
                bigFinger3_Y = 0
                secFinger5_X = 0 #二拇指點5
                secFinger5_Y = 0
                thirdFinger9_X = 0 #三拇指點9
                thirdFinger9_Y = 0
                fourthFinger13_X = 0 #四拇指點13
                fourthFinger13_Y = 0
                fifthFinger17_X = 0 #五拇指點17
                fifthFinger17_Y = 0
                #xx = 0
                #yy = 0
                for i, lm in enumerate(handLms.landmark):
                    xPos = round(lm.x * imgWidth)
                    yPos = round(lm.y * imgHeight)
                    if i == 0:
                        originx = xPos
                        originy = yPos
                    #if i == 2:
                        #xx = xPos
                        #yy = yPos
                    if i == 3:
                        bigFinger3_X = xPos
                        bigFinger3_Y = yPos
                        #if (xx-xPos) != 0:
                            #print("big finger:", getValueWithM(xPos, yPos, -1* (yy-yPos)/(xx-xPos),img))
                        #else:
                            #print("big finger:", getValueWithM(xPos, yPos, infinity,img))
                    if i == 4:
                        bigFinger4_X = xPos
                        bigFinger4_Y = yPos
                    if i == 5:
                        secFinger5_X = xPos #二拇指點5
                        secFinger5_Y = yPos
                    if i == 6:
                        if (secFinger5_X-xPos) != 0:
                            total += getValueWithM(xPos, yPos, -1* (secFinger5_Y-yPos)/(secFinger5_X-xPos),img)
                        else:
                            total += getValueWithM(xPos, yPos, infinity,img)
                        print("key: ", i, ", total: ", total)
                    if i == 9:
                        thirdFinger9_X = xPos #三拇指點9
                        thirdFinger9_Y = yPos
                    if i == 10:
                        if (thirdFinger9_X-xPos) != 0:
                            total += getValueWithM(xPos, yPos, -1* (thirdFinger9_Y-yPos)/(thirdFinger9_X-xPos),img)
                        else:
                            total += getValueWithM(xPos, yPos, infinity,img)
                        print("key: ", i, ", total: ", total)
                    if i == 13:
                        fourthFinger13_X = xPos #四拇指點13
                        fourthFinger13_Y = yPos
                    if i == 14:
                        if (fourthFinger13_X-xPos) != 0:
                            total += getValueWithM(xPos, yPos, -1* (fourthFinger13_Y-yPos)/(fourthFinger13_X-xPos),img)
                        else:
                            total += getValueWithM(xPos, yPos, infinity,img)
                        print("key: ", i, ", total: ", total)
                    if i == 17:
                        fifthFinger17_X = xPos #五拇指點17
                        fifthFinger17_Y = yPos
                    if i == 18:
                        if (fifthFinger17_X-xPos) != 0:
                            total += getValueWithM(xPos, yPos, -1* (fifthFinger17_Y-yPos)/(fifthFinger17_X-xPos),img)
                        else:
                            total += getValueWithM(xPos, yPos, infinity,img)
                        print("key: ", i, ", total: ", total)                     
                        
                        
                total = total * (20 / 19)
                m = find_m(originx, originy + round(img.shape[0]/6), img)[0] # 6是參數, 視實際拍攝圖片決定
                cun = total * 1/5
                guan = total * 1/2
                chi = total * 33/40
                cunx = cun / ((m*m+1)**(0.5))
                cuny = round(m * cunx)
                cunx = round(cunx)
                guanx = guan / ((m*m+1)**(0.5))
                guany = round(m * guanx)
                guanx = round(guanx)
                chix = chi / ((m*m+1)**(0.5))
                chiy = round(m * chix)
                chix = round(chix)
                if m < 0:
                    cunx = originx + cunx
                    cuny = originy - cuny
                    guanx = originx + guanx
                    guany = originy - guany
                    chix = originx + chix
                    chiy = originy - chiy
                if m > 0:
                    cunx = originx - cunx
                    cuny = originy + cuny
                    guanx = originx - guanx
                    guany = originy + guany
                    chix = originx - chix
                    chiy = originy + chiy
                #大拇指4和3的間距
                shift = dist((bigFinger4_X, bigFinger4_Y), (bigFinger3_X, bigFinger3_Y))/2
                shift_m = -1 / m
                shift_x = 0
                shift_y = 0
                shift_x = round(shift / ((shift_m*shift_m+1)**(0.5)))
                shift_y = round(shift_m * shift_x)
                #尚未左右移動的點
                cv2.circle(img, (cunx, cuny), 5, preTargetStyle, cv2.FILLED)
                cv2.circle(img, (guanx, guany), 5, preTargetStyle, cv2.FILLED)
                cv2.circle(img, (chix, chiy), 5, preTargetStyle, cv2.FILLED)
                #根據比例左右移動後的點
                if bigFinger4_X - originx >= 0:
                    cv2.circle(img, (cunx + shift_x, cuny - shift_y), 5, preTargetStyle, cv2.FILLED)
                    cv2.circle(img, (guanx + shift_x, guany - shift_y), 5, preTargetStyle, cv2.FILLED)
                    cv2.circle(img, (chix + shift_x, chiy - shift_y), 5, preTargetStyle, cv2.FILLED)
                else:
                    cv2.circle(img, (cunx - shift_x, cuny - shift_y), 5, preTargetStyle, cv2.FILLED)
                    cv2.circle(img, (guanx - shift_x, guany - shift_y), 5, preTargetStyle, cv2.FILLED)
                    cv2.circle(img, (chix - shift_x, chiy - shift_y), 5, preTargetStyle, cv2.FILLED)
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS, handLmsStyle, handConStyle)
        
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, f"FPS : {int(fps)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow('img', img)

    if cv2.waitKey(1) == ord('q'):
        break