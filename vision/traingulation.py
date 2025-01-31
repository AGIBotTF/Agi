import numpy as np

def find_depth(left_point, right_point, left_img, right_img, baseline, f, alpha):
    _, width_left, _ = left_img.shape
    _, width_right, _ = right_img.shape

    if width_left == width_right:
        f_pixel = (width_left / 2) / np.tan(alpha / 2 * np.pi / 180)

    else:
        print("Left and right images have different resolutions.")

    print(left_point, right_point)

    x_left = left_point
    x_right = right_point

    disparity = abs(x_left - x_right)

    zDepth = (baseline * f_pixel) / disparity
    
    return zDepth