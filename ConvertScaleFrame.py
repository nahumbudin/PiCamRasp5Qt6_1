import cv2
import numpy as np
from PyQt6 import QtGui


def convert_and_scale_frame(frame, target_width, target_height):
    """ Convert the frame to QPixmap using several steps.
        Output image size is scaled to the display window size."""
    img = np.array(frame)
    img_height, img_width, img_colors = img.shape

    scale_w = float(target_width) / float(img_width)
    scale_h = float(target_height) / float(img_height)
    scale = min([scale_w, scale_h])
    if scale == 0:
        scale = 1

    # scale = 1

    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    height, width, bpc = img.shape
    bpl = bpc * width
    image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format.Format_RGBA8888)

    if not (height > target_height or width > target_width):
        pix = QtGui.QPixmap(image)
        return pix, scale
    else:
        print("Illegal scaled frame size")
        return

