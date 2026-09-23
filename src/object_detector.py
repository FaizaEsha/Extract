"""
object_detector.py
-------------------
Path 2 of Project 4: Object Detection with a pre-trained MobileNet-SSD
(trained on the PASCAL VOC dataset — 20 object classes).

Implements exactly the steps named in the brief:
  Step 1: Blob Construction   -> cv2.dnn.blobFromImage (mean subtraction,
                                   300x300 resize)
  Step 2: Single-shot forward  -> one forward pass through the network
  Step 3: Softmax / confidence -> every detection carries a probability
  Step 4: 80% confidence gate  -> low-confidence detections are dropped
"""

import cv2
import numpy as np

# The 20 VOC classes chuanqi305/MobileNet-SSD was trained on, in the
# exact index order the network's output layer uses (index 0 = background).
VOC_CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle",
    "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse",
    "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
    "tvmonitor",
]

CONFIDENCE_GATE = 0.80  # 80% — the "absolute minimum standard" from the brief.

INPUT_SIZE = (300, 300)
MEAN_SUBTRACTION = 127.5  # matches the training normalization for this model
SCALE_FACTOR = 1 / 127.5


def load_model(prototxt_path: str, caffemodel_path: str):
    """Loads the pre-trained MobileNet-SSD network via cv2.dnn -- the
    'Transfer Learning' step: we inherit millions of images' worth of
    learned features instead of training from scratch."""
    net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
    return net


def detect(net, image_bgr: np.ndarray, confidence_gate: float = CONFIDENCE_GATE) -> list:
    """Runs the full detection pipeline and returns only detections that
    clear the confidence gate. Each result is a dict with class label,
    confidence, and pixel-space bounding box (x, y, w, h)."""
    (h, w) = image_bgr.shape[:2]

    # Step 1: Blob Construction — resize to the network's expected
    # 300x300 input and apply mean subtraction, as specified in the brief.
    blob = cv2.dnn.blobFromImage(
        image_bgr, SCALE_FACTOR, INPUT_SIZE,
        (MEAN_SUBTRACTION, MEAN_SUBTRACTION, MEAN_SUBTRACTION),
        swapRB=False, crop=False,
    )

    # Step 2: Single forward pass (the "SSD Way" vs. old multi-pass detectors).
    net.setInput(blob)
    raw_detections = net.forward()

    results = []
    for i in range(raw_detections.shape[2]):
        confidence = float(raw_detections[0, 0, i, 2])
        if confidence < confidence_gate:
            continue  # The 80% gate: drop anything below the standard.

        class_id = int(raw_detections[0, 0, i, 1])
        label = VOC_CLASSES[class_id] if class_id < len(VOC_CLASSES) else "unknown"

        # Step 3: Coordinate Scaling — the network outputs normalized
        # (0-1) coordinates; multiply by actual pixel width/height.
        box = raw_detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (x1, y1, x2, y2) = box.astype("int")
        x1, y1 = max(0, x1), max(0, y1)

        results.append({
            "label": label,
            "confidence": confidence,
            "box": (int(x1), int(y1), int(x2 - x1), int(y2 - y1)),
        })

    return results


def draw_annotations(image_bgr: np.ndarray, detections: list) -> np.ndarray:
    """Draws a labeled bounding box for every surviving detection."""
    annotated = image_bgr.copy()
    palette = [
        (60, 180, 75), (0, 130, 200), (245, 130, 48),
        (145, 30, 180), (70, 240, 240), (240, 50, 230),
    ]
    for idx, det in enumerate(detections):
        x, y, w, h = det["box"]
        color = palette[idx % len(palette)]
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 3)
        text = f"{det['label']}: {det['confidence']*100:.1f}%"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(annotated, (x, y - th - 12), (x + tw + 8, y), color, -1)
        cv2.putText(
            annotated, text, (x + 4, y - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA
        )
    return annotated
