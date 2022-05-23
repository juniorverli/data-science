import cv2
import pickle
import cvzone
import numpy as np
import morse_code

with open('NetflixLogoPos', 'rb') as f:
        posList = pickle.load(f)

width, height = 150, 60

def checkNetflixLogo(imgPro):
    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y:y+height, x:x+width]
        cv2.imshow(str(x*y),imgCrop)
        count = cv2.countNonZero(imgCrop)
        cvzone.putTextRect(img, str(count), (x,y+height-10), scale = 1, thickness=1, offset=0)

        if count > 3000:
            color = (0,255,0)
            tickness = 1
        else:
            color = (0,0,255)
            tickness = 1
        cv2.rectangle(img,pos,(pos[0]+width, pos[1]+height), (color),tickness)

    return count

COUNTER = 0
BREAK_COUNTER = 0
OPEN_COUNTER = 0
CLOSED = False
WORD_PAUSE = False
PAUSED = False
AR_CONSEC_FRAMES = 2
AR_CONSEC_FRAMES_CLOSED = 5
PAUSE_CONSEC_FRAMES = 9
WORD_PAUSE_CONSEC_FRAMES = 9
BREAK_LOOP_FRAMES = 120
total_morse = ""
morse_word = ""
morse_char = ""

cap = cv2.VideoCapture('assets/StrangerThings4.mp4')
#time.sleep(1.0)

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    cv2.waitKey(10)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25,15)
    imgMedian = cv2.medianBlur(imgThreshold,5)
    kernel = np.ones((3,3),np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    
    if checkNetflixLogo(imgDilate) < 3000:
        COUNTER += 1
        BREAK_COUNTER += 1
        if COUNTER >= AR_CONSEC_FRAMES:
            CLOSED = True
        # Reset morse that appears on screen if it had just been "/"
        if not PAUSED:
            morse_char = ""
        # Eyes closed for long enough to close program. 
        if (BREAK_COUNTER >= BREAK_LOOP_FRAMES):
            break
        # otherwise, the eye aspect ratio is not below the blink
        # threshold
    else:
        # Eyes weren't closed for that long 
        if (BREAK_COUNTER < BREAK_LOOP_FRAMES):
            BREAK_COUNTER = 0
            OPEN_COUNTER += 1
        # Dash detected as eyes closed for long time.
        if COUNTER >= AR_CONSEC_FRAMES_CLOSED:
            morse_word += "-"
            total_morse += "-"
            morse_char += "-"
        # reset the eye frame counter
            COUNTER = 0
            CLOSED = False
            PAUSED = True
            OPEN_COUNTER = 0
        # Dot detected as eyes closed for short time.
        elif CLOSED:
            morse_word += "."
            total_morse += "."
            morse_char += "."
            COUNTER = 1
            CLOSED = False
            PAUSED = True
            OPEN_COUNTER = 0
        # Only add space between chars if char previously 
        # detected and eyes open for > PAUSE_CONSEC_FRAMES.
        elif PAUSED and (OPEN_COUNTER >= 
            PAUSE_CONSEC_FRAMES):
            morse_word += "/"
            total_morse += "/"
            morse_char = "/"
            PAUSED = False
            WORD_PAUSE = True
            CLOSED = False
            OPEN_COUNTER = 0
            morse_word = ""
            # Add space between words if char space prev added and 
            # eyes open for >= WORD_PAUSE_CONSEC_FRAMES after 
            # already opened for PAUSE_CONSEC_FRAMES .
        elif (WORD_PAUSE and OPEN_COUNTER >= WORD_PAUSE_CONSEC_FRAMES):
        # "/" already in str from char pause, "¦" is 
        # converted to a " " (space) char.
            total_morse += "¦/"
            morse_char = ""
            WORD_PAUSE = False
            CLOSED = False
            OPEN_COUNTER = 0

        # draw the computed eye aspect ratio for the frame and display 
        # the recently detected morse code
        cv2.putText(img, "Codigo Morse: {}".format(morse_char), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, "NetflixLogo: {:.2f}".format(checkNetflixLogo(imgDilate)), (600, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, "Mensagem: {}".format(morse_code.from_morse(total_morse)), (10,100), 
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
    cv2.imshow('Image', img)
    cv2.waitKey(1)

cv2.destroyAllWindows()
print("Codigo Morse: {}".format(morse_code.from_morse(total_morse)))