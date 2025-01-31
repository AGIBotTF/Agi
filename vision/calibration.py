import numpy as np
import cv2

cv_file = cv2.FileStorage("stereo_calibration.xml", cv2.FILE_STORAGE_READ)

stereoMapLx = cv_file.getNode("stereoMapLx").mat()
stereoMapLy = cv_file.getNode("stereoMapLy").mat()
stereoMapRx = cv_file.getNode("stereoMapRx").mat()
stereoMapRy = cv_file.getNode("stereoMapRy").mat()

def undistortRectify(frame_left, frame_right):
    # Undistort and rectify frames
    frame_left_rect = cv2.remap(frame_left, stereoMapLx, stereoMapLy, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    frame_right_rect = cv2.remap(frame_right, stereoMapRx, stereoMapRy, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

    return frame_left_rect, frame_right_rect