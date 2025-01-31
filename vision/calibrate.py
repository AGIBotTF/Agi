import cv2
import numpy as np
from time import sleep

# Checkerboard dimensions
CHECKERBOARD = (7, 3)  # 7 internal corners horizontally, 3 vertically (for an 8x8 checkerboard)

# Criteria for subpixel corner detection
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points (3D points in the real world)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[1], 0:CHECKERBOARD[0]].T.reshape(-1, 2)

# Arrays to store object points and image points for both cameras
objpoints = []  # 3D points in world space
imgpoints_left = []  # 2D points in the left image
imgpoints_right = []  # 2D points in the right image

# Open stereo cameras
cap_left = cv2.VideoCapture(1)
cap_right = cv2.VideoCapture(0)

if not cap_left.isOpened() or not cap_right.isOpened():
    print("Error: Could not open one or both cameras.")
    exit()

frame_count = 0
while True:
    ret_left, frame_left = cap_left.read()
    ret_right, frame_right = cap_right.read()

    if not ret_left or not ret_right:
        print("Error: Failed to capture frames.")
        break

    # Convert to grayscale
    gray_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret_left, corners_left = cv2.findChessboardCorners(gray_left, CHECKERBOARD, None)
    ret_right, corners_right = cv2.findChessboardCorners(gray_right, CHECKERBOARD, None)

    if ret_left and ret_right:
        objpoints.append(objp)

        corners2_left = cv2.cornerSubPix(gray_left, corners_left, (11, 11), (-1, -1), criteria)
        corners2_right = cv2.cornerSubPix(gray_right, corners_right, (11, 11), (-1, -1), criteria)

        imgpoints_left.append(corners2_left)
        imgpoints_right.append(corners2_right)

        # Draw and display the corners
        cv2.drawChessboardCorners(frame_left, CHECKERBOARD, corners2_left, ret_left)
        cv2.drawChessboardCorners(frame_right, CHECKERBOARD, corners2_right, ret_right)

        frame_count += 1
        print(f"Frames captured: {frame_count}")
        
    else:
        print("Chessboard not detected in one or both frames.")

    # Display frames
    cv2.imshow('Left Camera', frame_left)
    cv2.imshow('Right Camera', frame_right)

    # Exit loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(0) & 0xFF == ord('e'):
        # discard last frame
        if frame_count == 0:
            print("No frames to discard.")
            continue
        objpoints.pop()
        imgpoints_left.pop()
        imgpoints_right.pop()
        frame_count -= 1
        print("Frame discarded")

    if frame_count >= 5:
        print("5 frames captured. Exiting...")
        break
    

cap_left.release()
cap_right.release()
cv2.destroyAllWindows()

# Check if sufficient frames were captured
if len(objpoints) < 5:
    print("Error: Not enough frames captured for calibration. Please try again.")
    exit()

print("Calibrating cameras...")

# Perform calibration
ret_left, mtx_left, dist_left, rvecs_left, tvecs_left = cv2.calibrateCamera(
    objpoints, imgpoints_left, gray_left.shape[::-1], None, None)
ret_right, mtx_right, dist_right, rvecs_right, tvecs_right = cv2.calibrateCamera(
    objpoints, imgpoints_right, gray_right.shape[::-1], None, None)

optimal_camera_matrix_left, roi_left = cv2.getOptimalNewCameraMatrix(mtx_left, dist_left, gray_left.shape[::-1], 1,
                                                                     gray_left.shape[::-1])
optimal_camera_matrix_right, roi_right = cv2.getOptimalNewCameraMatrix(mtx_right, dist_right, gray_right.shape[::-1], 1,
                                                                       gray_right.shape[::-1])


print("Stereo calibration...")

flags = 0
# flags |= cv2.CALIB_FIX_INTRINSIC

# Stereo calibration
ret, camera_matrix1, dist_coeffs1, camera_matrix2, dist_coeffs2, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpoints_left, imgpoints_right, optimal_camera_matrix_left, dist_left, optimal_camera_matrix_right, dist_right, gray_left.shape[::-1],
    criteria=criteria, flags=flags)

print("Camera Matrix 1 (Left Camera):")
print(camera_matrix1)
print("Distortion Coefficients 1 (Left Camera):")
print(dist_coeffs1)

print("Camera Matrix 2 (Right Camera):")
print(camera_matrix2)
print("Distortion Coefficients 2 (Right Camera):")
print(dist_coeffs2)

print("Rectifying cameras...")
rectifyScale = 1
R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(camera_matrix1, dist_coeffs1, camera_matrix2, dist_coeffs2,
                                                  gray_left.shape[::-1], R, T, rectifyScale, (0,0))

stereoMapL = cv2.initUndistortRectifyMap(camera_matrix1, dist_coeffs1, R1, P1, gray_left.shape[::-1], cv2.CV_16SC2)
stereoMapR = cv2.initUndistortRectifyMap(camera_matrix2, dist_coeffs2, R2, P2, gray_right.shape[::-1], cv2.CV_16SC2)

# Assuming you already have 'frame_left' and 'frame_right' captured
frame_left_rect = cv2.remap(frame_left, stereoMapL[0], stereoMapL[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
frame_right_rect = cv2.remap(frame_right, stereoMapR[0], stereoMapR[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

# Show the original frames
cv2.imshow('Original Left', frame_left)
cv2.imshow('Original Right', frame_right)

# Show the rectified frames
cv2.imshow('Rectified Left', frame_left_rect)
cv2.imshow('Rectified Right', frame_right_rect)

cv2.waitKey(0)
cv2.destroyAllWindows()


print("Calibration complete. Saving parameters...")

cv_file = cv2.FileStorage("stereo_calibration.xml", cv2.FILE_STORAGE_WRITE)

cv_file.write("stereoMapLx", stereoMapL[0])
cv_file.write("stereoMapLy", stereoMapL[1])
cv_file.write("stereoMapRx", stereoMapR[0])
cv_file.write("stereoMapRy", stereoMapR[1])

cv_file.release()
