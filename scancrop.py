import os
import cv2 as cv
import numpy as np
from utils import *


def get_roi(contours):
    """Get region of interests.

    Args:
        contours: cv2 contours.

    Returns:
        roi: Region of interests.
        max_area: Area of the biggest roi.
    """
    boxes = []
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        boxes.append([[x, y], [x + w, y + h]])

    roi, max_area = merge_boxes(boxes)
    return roi, max_area


def crop_scans(img, candidates, thresh=100000):
    """Crop scan areas in image.

    Args:
        img: Image to crop.
        candidates: Candidates for cropping.
        thresh: Threshold of minimum candidate area.

    Return:
        scans: Scan areas in input image.
    """
    scans = []
    for candidate in candidates:
        if rect_area(candidate) > thresh:
            tl, br = candidate
            x, y = tl[0], tl[1]
            w, h = br[0] - tl[0], br[1] - tl[1]
            scans.append(img[y:y+h, x:x+w, :])

    return scans


def find_scans(img):
    """Find scan areas in image.

    Args:
        img: Original scan image.

    Return:
        scans: Target scan areas in input image.
    """
    # blur image to suppress noise
    blur = cv.medianBlur(img, 5)
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    # make backgound 0 so that we can retrieve inside photos' external contours
    ret, thresh = cv.threshold(gray, 200, 255, cv.THRESH_BINARY_INV)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    roi, max_area = get_roi(contours)

    # plot region of interest
    # plot_roi(blur, roi)

    # area of each scans should be at least some ratio to the max area
    scans = crop_scans(img, roi, max_area * 0.4)
    return scans


def process_file(src_dir, fname, out_dir='./crop'):
    """Process given file.

    Args:
        src_dir: Source directory of scan image.
        fname: Image name.
        out_dir: Output directory of crop image.
    """
    img = cv.imread(os.path.join(src_dir, fname))
    scans = find_scans(img)
    for i, scan in enumerate(scans):
        cv.imwrite(os.path.join(out_dir, f'{fname[:-4]}_{i+1}.jpg'), scan)


if __name__ == "__main__":
    src_dir = './scan'
    fname = 'Image00031.jpg'
    out_dir = ''
    process_file(src_dir, fname, out_dir)
