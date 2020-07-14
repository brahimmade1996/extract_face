import cv2
from mtcnn.mtcnn import MTCNN
import numpy as np
import time
import imutils


def getEyeCoords(co_ord, face_width, face_height):
    x = co_ord[0]
    y = co_ord[1]
    wrec = int(face_width / 4)
    hrec = int(face_height / 8)
    ex = int(x - (wrec / 2))
    ey = int(y - (hrec / 2))
    return (ex, ey), (ex + wrec, ey + hrec)


def getMouthCoords(leftm, rightm, nose, face_width, face_height):
    wrec = rightm[0] - leftm[0] + int(face_width / 10)
    hrec = int(1.5 * (leftm[1] - nose[1] - (face_height / 10)))
    mx = leftm[0] - int(face_width / 20)
    # mx = nose[0] - int(wrec / 2) - int(face_width / 20)
    my = nose[1] + int(face_height / 8)
    return (mx, my), (mx + wrec, my + hrec)


def extractRoi(img, detections, resize):
    face = []
    roilef = []
    roiref = []
    roimf = []
    face_coords = []
    le_coords = []
    re_coords = []
    m_coords = []

    # check to see if detections are present:
    if len(detections) > 0:
        # loop through results
        for result in detections:
            rect = result['box']
            keypoints = result['keypoints']

            # get face coordinates
            x, y, w, h = rect[0], rect[1], rect[2], rect[3]
            face_coords.append([(x, y), (x+w, y+h)])

            try:
                # get face ROI
                face.append(imutils.resize(img[y:y+h, x:x+w], width=resize, inter=cv2.INTER_CUBIC))

            except cv2.error:
                time.sleep(0.1)

            # initialize mouth and nose coords as 0
            mright, mleft, nose = 0, 0, 0
            for n, v in keypoints.items():

                if n == 'left_eye':
                    # get left eye coordinates and ROI
                    eye1, eye2 = getEyeCoords(v, w, h)
                    le_coords.append([eye1, eye2])
                    try:
                        roile = img[eye1[1]:eye2[1], eye1[0]:eye2[0]]
                        roile = imutils.resize(roile, width=resize, inter=cv2.INTER_CUBIC)
                        roilef.append(roile)

                    except cv2.error:
                        time.sleep(0.1)

                if n == 'right_eye':
                    # get right eye coordinates and ROI
                    eye1, eye2 = getEyeCoords(v, w, h)
                    re_coords.append([eye1, eye2])

                    try:
                        roire = img[eye1[1]:eye2[1], eye1[0]:eye2[0]]
                        roire = imutils.resize(roire, width=resize, inter=cv2.INTER_CUBIC)
                        roiref.append(roire)

                    except cv2.error:
                        time.sleep(0.1)

                # save nose coords for later
                if n == 'nose':
                    nose = v

                if n == 'mouth_left':
                    mleft = v

                if n == 'mouth_right':
                    mright = v

                    # get mouth coordinates and ROI
                    mouth1, mouth2 = getMouthCoords(mleft, mright, nose, w, h)
                    m_coords.append([mouth1, mouth2])

                    try:
                        roim = img[mouth1[1]:mouth2[1], mouth1[0]:mouth2[0]]
                        roim = imutils.resize(roim, width=resize, inter=cv2.INTER_CUBIC)
                        roimf.append(roim)

                    except cv2.error:
                        time.sleep(0.1)

        return face, roilef, roiref, roimf, face_coords, le_coords, re_coords, m_coords

    else:
        return face, roilef, roiref, roimf, face_coords, le_coords, re_coords, m_coords


detector = MTCNN()

roiM = None
roiRE = None
roiLE = None
grayM = None
grayRE = None
grayLE = None
openLE = False
openRE = False
faes = None

image_width = 500

cap = cv2.VideoCapture(0)

while 1:
    ret, img = cap.read()
    if ret:
        img = imutils.resize(img, width=image_width)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clone = img.copy()

        results = detector.detect_faces(img)

        roiF, roiLES, roiRES, roiMS, foo1, foo2, foo3, foo4 = extractRoi(img, results, 250)

        if len(roiF) > 0:
            roiLE = roiLES[0]
            roiRE = roiRES[0]
            roiM = roiMS[0]
            faes = roiF[0]

        try:
            cv2.imshow('mouth', roiM)
            cv2.imshow('leftEye', roiLE)
            cv2.imshow('rightEye', roiRE)
            cv2.imshow('face', faes)

        except cv2.error:
            time.sleep(0.1)

        cv2.imshow('original', img)
        cv2.imshow('out', clone)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
