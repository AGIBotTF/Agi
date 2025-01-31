import sys
import cv2
import numpy as np
import time
import imutils

import traingulation as tri
import calibration as cal

import mediapipe as mp

mp_facedetector = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

cap_left = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap_right = cv2.VideoCapture(1, cv2.CAP_DSHOW)


frame_rate = 30
B = 5
f = 8
alpha = 56.6

with mp_facedetector.FaceDetection(min_detection_confidence=0.5) as face_detector:
    while(cap_right.isOpened() and cap_left.isOpened()):
        ret_left, frame_left = cap_left.read()
        ret_right, frame_right = cap_right.read()

        if not ret_left or not ret_right:
            print("Error: Failed to capture frames.")
            break

        # flip the frames

        # frame_left, frame_right = cal.undistortRectify(frame_left, frame_right)
        frame_right = cv2.flip(frame_right, 0)
        # frame_left = cv2.flip(frame_left, 1)

        start = time.time()
        frame_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2RGB)
        frame_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2RGB)

        results_left = face_detector.process(frame_left)
        results_right = face_detector.process(frame_right)

        frame_left = cv2.cvtColor(frame_left, cv2.COLOR_RGB2BGR)
        frame_right = cv2.cvtColor(frame_right, cv2.COLOR_RGB2BGR)

        # CALCULATE DEPTH

        center_left = 0
        center_right = 0

        if results_left.detections:
            for id, detection in enumerate(results_left.detections):
                mp_draw.draw_detection(frame_left, detection)

                bBox = detection.location_data.relative_bounding_box

                h, w, c = frame_left.shape

                boundBox = int(bBox.xmin * w), int(bBox.ymin * h), int(bBox.width * w), int(bBox.height * h)

                center_left = int(bBox.xmin * w + bBox.width * w / 2)

                # cv2.putText(frame_left, f"{detection.score[0] * 100:.2f}%", (boundBox[0], boundBox[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

        if results_right.detections:
            for id, detection in enumerate(results_right.detections):
                mp_draw.draw_detection(frame_right, detection)

                bBox = detection.location_data.relative_bounding_box

                h, w, c = frame_right.shape

                boundBox = int(bBox.xmin * w), int(bBox.ymin * h), int(bBox.width * w), int(bBox.height * h)

                center_right = int(bBox.xmin * w + bBox.width * w / 2)

                # cv2.putText(frame_right, f"{detection.score[0] * 100:.2f}%", (boundBox[0], boundBox[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

        if center_left and center_right:
            depth = tri.find_depth(center_left, center_right, frame_left, frame_right, B, f, alpha)
            # depth = 0

            cv2.putText(frame_left, f"Depth: {depth:.2f} cm", (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
            cv2.putText(frame_right, f"Depth: {depth:.2f} cm", (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

            print(f"Depth: {depth:.2f} cm")

        end = time.time()
        totalTime = end - start
        fps = 1 / totalTime

        cv2.putText(frame_left, f"FPS: {fps:.2f}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
        cv2.putText(frame_right, f"FPS: {fps:.2f}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

        cv2.imshow('Left Camera', frame_left)
        cv2.imshow('Right Camera', frame_right)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap_left.release()
cap_right.release()