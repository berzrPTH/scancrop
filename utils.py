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
    tl1, br1 = source
    tl2, br2 = target
    if tl1[0] >= br2[0] or tl2[0] >= br1[0]:
        return False
    if tl1[1] >= br2[1] or tl2[1] >= br1[1]:
        return False
    return True


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


def merge_boxes(boxes, img=None):
    """Merge overlapping boxes.

    Args:
        boxes: List of boxes.
        img: Image for plot if needed.

    Returns:
        boxes: List of boxes after merge.
        max_area: Area of the biggest box in return boxes.
    """
    max_area = 0
    finished = False

    # merge box from large to small, which accelerate the process
    boxes.sort(key=lambda box: rect_area(box))

    # find all possible pairs and find if there are overlapping
    while not finished:
        finished = True
        idx = len(boxes) - 1

        while idx >= 0:
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

            idx -= 1

    return boxes, max_area
