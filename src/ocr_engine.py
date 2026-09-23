"""
ocr_engine.py
-------------
Path 1 of Project 4: Optical Character Recognition.

Wraps pytesseract (Google's Tesseract engine — a CNN + bi-directional
LSTM pipeline under the hood) with:
  - PSM (Page Segmentation Mode) auto-selection, as flagged in the
    "Tuning the PSM" slide of the brief
  - per-word confidence scoring
  - the 80% confidence gate required by grading criterion #3
"""

import cv2
import numpy as np
import pytesseract
from pytesseract import Output

# PSM modes from the brief, tried in order of "most specific" first.
PSM_CANDIDATES = {
    6: "Single uniform block of text (book pages / invoices)",
    3: "Fully automatic page segmentation (varied layouts)",
    11: "Sparse, scattered text (loose invoices)",
    7: "Single text line (headers / plates)",
}

CONFIDENCE_GATE = 80.0  # The "absolute minimum standard" set by the brief.


def _run_with_psm(binary_image: np.ndarray, psm: int) -> dict:
    config = f"--oem 3 --psm {psm}"
    data = pytesseract.image_to_data(
        binary_image, config=config, output_type=Output.DICT
    )
    return data


def extract_text(binary_image: np.ndarray) -> dict:
    """Runs OCR across several PSM modes and keeps whichever mode
    produces the highest mean confidence on non-empty tokens. Returns
    a report containing the full text, per-word boxes/confidences, the
    winning PSM, and whether the 80% gate was passed.
    """
    best = None

    for psm, _description in PSM_CANDIDATES.items():
        data = _run_with_psm(binary_image, psm)

        words, confs, boxes = [], [], []
        for i, txt in enumerate(data["text"]):
            txt = txt.strip()
            conf = float(data["conf"][i])
            if txt and conf > 0:
                words.append(txt)
                confs.append(conf)
                boxes.append((
                    data["left"][i], data["top"][i],
                    data["width"][i], data["height"][i]
                ))

        mean_conf = float(np.mean(confs)) if confs else 0.0

        if best is None or mean_conf > best["mean_confidence"]:
            best = {
                "psm_used": psm,
                "psm_description": PSM_CANDIDATES[psm],
                "words": words,
                "confidences": confs,
                "boxes": boxes,
                "mean_confidence": mean_conf,
                "full_text": " ".join(words),
            }

    best["confidence_gate"] = CONFIDENCE_GATE
    best["passed_gate"] = best["mean_confidence"] >= CONFIDENCE_GATE
    return best


def draw_annotations(original_bgr: np.ndarray, report: dict) -> np.ndarray:
    """Draws a box around every recognized word, colored green if that
    word individually cleared the 80% gate and amber otherwise, so the
    output is a legible, self-explaining visual confirmation."""
    annotated = original_bgr.copy()
    for word, conf, (x, y, w, h) in zip(
        report["words"], report["confidences"], report["boxes"]
    ):
        color = (60, 180, 75) if conf >= CONFIDENCE_GATE else (0, 165, 255)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            annotated, f"{int(conf)}%", (x, max(0, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA
        )
    return annotated
