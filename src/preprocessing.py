"""
preprocessing.py
-----------------
Implements the "Logic Skeleton" pre-processing pipeline required by
Project 4:

    Step 1: Grayscale Conversion   -> collapse the 3D RGB matrix to 1D
    Step 2: Gaussian Blur          -> suppress sensor / chromatic noise
    Step 3: Deskewing              -> snap tilted text to a horizontal baseline
    Step 4: Adaptive Thresholding  -> force every pixel to a binary decision
                                       (Otsu's method, as specified in the brief)

Every function returns a numpy array (OpenCV image) AND is written so that
each intermediate stage can be saved/displayed independently, which is
required for grading criterion #2 ("Pre-Processing Integrity") and #4
("Visual Confirmation").
"""

import cv2
import numpy as np


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Step 1: Collapse the 3-channel (B, G, R) matrix into a single
    intensity channel. Removes color data that is irrelevant to shape
    recognition and reduces the problem to a 1D intensity matrix."""
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(gray: np.ndarray, kernel: tuple = (5, 5)) -> np.ndarray:
    """Step 2: Gaussian Blur. Smooths micro-imperfections and sensor
    noise so thresholding doesn't latch onto speckle artifacts."""
    return cv2.GaussianBlur(gray, kernel, 0)


def deskew(gray: np.ndarray) -> np.ndarray:
    """Step 3: Deskewing. Calculates the dominant rotation angle of the
    text block (via the minimum-area bounding rectangle of foreground
    pixels) and rotates the image so the baseline is horizontal again.
    """
    # Invert + threshold to find foreground (text/ink) pixels.
    inv = cv2.bitwise_not(gray)
    thresh = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 20:
        # Not enough foreground signal to safely estimate an angle.
        return gray

    angle = cv2.minAreaRect(coords)[-1]

    # cv2.minAreaRect returns an angle in [-90, 0); normalize it so we
    # rotate by the *smallest* correction rather than overshooting by 90°.
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        gray, matrix, (w, h),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def adaptive_threshold(gray: np.ndarray) -> tuple:
    """Step 4: Adaptive Thresholding via Otsu's method. Forces every
    pixel to choose a side (pure black or white), producing the crisp
    contrast OCR engines need. Returns (binary_image, computed_cutoff).
    """
    cutoff, binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )
    return binary, cutoff


def run_pipeline(image: np.ndarray) -> dict:
    """Runs the full 4-stage pipeline and returns every intermediate
    stage so the caller can save/display each one for grading
    criterion #2 (Pre-Processing Integrity)."""
    stage_gray = to_grayscale(image)
    stage_blur = denoise(stage_gray)
    stage_deskewed = deskew(stage_blur)
    stage_binary, cutoff = adaptive_threshold(stage_deskewed)

    return {
        "grayscale": stage_gray,
        "blurred": stage_blur,
        "deskewed": stage_deskewed,
        "binary": stage_binary,
        "otsu_cutoff": cutoff,
    }
