import cv2 as cv
import numpy as np


def plot_roi(img, roi):
    """Plot region of interests on image.

    Args:
        img: Image to plot on.
        roi: Region of interests.
    """
    copy = np.copy(img)
    for box in roi:
        copy = plot_box(copy, box)
    cv.imshow('ROI', copy)
    cv.imwrite('ROI.jpg', copy)


def plot_box(img, box, color=(0, 255, 0)):
    copy = np.copy(img)
    cv.rectangle(copy, box[0], box[1], color, 1)
    return copy
