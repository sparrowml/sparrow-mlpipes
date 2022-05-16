import numpy as np
import numpy.typing as npt


def nms(
    boxes: npt.NDArray[np.float64],
    scores: npt.NDArray[np.float64],
    iou_threshold: float,
) -> npt.NDArray[np.int64]:
    """
    Remove overlapping boxes with non-max suppression.

    Parameters
    ----------
    boxes
        (n, 4) boxes in x, y, w, h format
    scores
        (n,) scores
    iou_threshold
        The IoU threshold above which to remove overlapping boxes

    Returns
    -------
    keep_boxes
        A set of boxes to keep
    """
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = x1 + boxes[:, 2]
    y2 = y1 + boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]  # get boxes with more ious first

    keep = []
    while order.size > 0:
        i = order[0]  # pick maxmum iou box
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)  # maximum width
        h = np.maximum(0.0, yy2 - yy1 + 1)  # maxiumum height
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= iou_threshold)[0]
        order = order[inds + 1]

    return np.array(keep).astype(np.int64)
