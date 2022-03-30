import cv2 as cv
import numpy as np


def rect_area(rect):
    """Evaluate rectangle area.

    Arg:
        rect: Iterable object for rectangle ((top, left), (bottom, right)).

    Return:
        Rectangle area.
    """
    tl, br = rect
    return (br[0] - tl[0]) * (br[1] - tl[1])


def is_overlap(source, target):
    """If the source and target rectangle overlap.

    Args:
        source: source rectangle (tl, br).
        target: target rectangle (tl, br).

    Return:
        True if overlap
    """
    tl, br = source
    tlx, brx = target
    if tl[0] <= tlx[0] <= br[0] and tl[1] <= tlx[1] <= br[1]:
        return True
    if tlx[0] <= tl[0] <= brx[0] and tlx[1] <= tl[1] <= brx[1]:
        return True

    return False


def find_overlaps(boxes, idx):
    """Find set of overlapping boxes with given index (exclusive).

    Args:
        boxes: Total boxes.
        idx: Given index.

    Return:
        overlaps: Set of indices of overlapping boxes.
    """
    overlaps = set()
    for i, box in enumerate(boxes):
        if i == idx:
            continue
        if is_overlap(boxes[idx], box):
            overlaps.add(i)

    return overlaps


def plot_roi(img, roi):
    """Plot region of interests on image.

    Args:
        img: Image to plot on.
        roi: Region of interests.
    """
    copy = np.copy(img)
    for r in roi:
        cv.rectangle(copy, r[0], r[1], (0, 200, 0), 2)
    cv.imshow('ROI', copy)
    cv.imwrite('./ROI.jpg', copy)
    cv.waitKey(0)


def merge_boxes(boxes):
    """Merge overlapping boxes.

    Arg:
        boxes: List of boxes.

    Returns:
        boxes: List of boxes after merge.
        max_area: Area of the biggest box in return boxes.
    """
    max_area = 0
    finished = False
    # find all possible pairs and find if there are overlapping
    while not finished:
        finished = True
        idx = 0
        while idx < len(boxes):
            max_area = max(max_area, rect_area(boxes[idx]))
            overlap_idx = find_overlaps(boxes, idx)
            # if there are overlapping boxes, form a new box include them
            if overlap_idx:
                overlap_idx.add(idx)
                overlap_boxes = [boxes[i] for i in overlap_idx]
                overlap_boxes = np.array(overlap_boxes).reshape((-1, 2))
                # the new box should be minimum
                top, left = np.min(overlap_boxes, axis=0)
                bot, right = np.max(overlap_boxes, axis=0)

                # update boxes by 1) remove overlapping boxes and
                boxes = [
                    box for i, box in enumerate(boxes) if i not in overlap_idx]
                # 2) add the new box we formed
                boxes.append([[top, left], [bot, right]])

                # new box added, need to check if there are new overlapping
                finished = False
                break

            idx += 1

    return boxes, max_area
