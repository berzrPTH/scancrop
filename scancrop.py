import os
import os.path as osp
import cv2 as cv
import numpy as np
import argparse
import errno
from tqdm import tqdm
from utils import *
from plot import *


parser = argparse.ArgumentParser()
parser.add_argument(
    '--dir', '-d', type=str, default='./',
    help='Specify the source directory.')
parser.add_argument(
    '--odir', '-o', type=str, default='./output',
    help='Specify the output directory.')
parser.add_argument(
    '--blur', '-b', type=int, default=5,
    help='Specify the size of blur kernel.' +
    '\nIf there exists lots of noise, we may need bigger value.' +
    '\n**Must be odd number greater than 1.**')
parser.add_argument(
    '--thresh', '-t', type=int, default=200,
    help='Specify the threshold of the backgound of scanned image.' +
    '\nBrighter the backgound, higher the value may set.' +
    '\n**Must be number in range [0, 255].**')
parser.add_argument(
    '--ratio', '-r', type=float, default=0.4,
    help='Specify the ratio of the area of smallest photo to biggest one' +
    '\n**Must be number in range [0.0, 1.0].**')

args = parser.parse_args()
EXTS = ('.jpg', '.jpeg', '.png', '.bmp')
SRCDIR = args.dir
OUTDIR = args.odir
BLUR = args.blur
THRESH = args.thresh
RATIO = args.ratio


def get_roi(contours, img=None):
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


def crop_scans(img, candidates, minimum=100000):
    """Crop scan areas in image.

    Args:
        img: Image to crop.
        candidates: Candidates for cropping.
        minimum: Threshold of minimum candidate area.

    Return:
        scans: Scan areas in input image.
    """
    scans = []
    for candidate in candidates:
        if rect_area(candidate) > minimum:
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
    blur = cv.medianBlur(img, BLUR)
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    # make backgound 0 so that we can retrieve inside photos' external contours
    ret, thresh = cv.threshold(gray, THRESH, 255, cv.THRESH_BINARY_INV)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    roi, max_area = get_roi(contours, blur)

    # plot region of interest
    # plot_roi(img, roi)

    # area of each scans should be at least some ratio to the max area
    scans = crop_scans(img, roi, max_area * RATIO)
    return scans


def process_file(src_dir, fname, out_dir='./crop'):
    """Process given file.

    Args:
        src_dir: Source directory of scan image.
        fname: Image name.
        out_dir: Output directory of crop image.
    """
    img = cv.imread(osp.join(src_dir, fname))
    scans = find_scans(img)
    for i, scan in enumerate(scans):
        cv.imwrite(osp.join(
            out_dir, f'{osp.splitext(fname)[0]}_{i+1}.jpg'), scan)


if __name__ == "__main__":
    try:
        os.mkdir(OUTDIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    fns = [fn for fn in os.listdir(SRCDIR) if fn.endswith(EXTS)]
    for fn in tqdm(fns):
        process_file(SRCDIR, fn, OUTDIR)
