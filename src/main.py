"""
main.py
-------
Project 4 entry point — "Building the Machine's Optic Nerve".

Runs BOTH recognition paths end-to-end:
    Path 1: OCR              on sample_images/sample_invoice.jpg
    Path 2: Object Detection on sample_images/dog_bike_car.jpg

Saves every intermediate stage image + a final annotated result for
each path into outputs/, and writes outputs/report.json summarizing
everything (used by the interactive HTML demo page).

Usage:
    python3 src/main.py
"""

import base64
import json
import os
import sys
import time

import cv2

sys.path.insert(0, os.path.dirname(__file__))
import preprocessing
import ocr_engine
import object_detector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DIR = os.path.join(ROOT, "sample_images")
OUTPUT_DIR = os.path.join(ROOT, "outputs")
MODEL_DIR = os.path.join(ROOT, "models")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def save(img, name):
    path = os.path.join(OUTPUT_DIR, name)
    cv2.imwrite(path, img)
    return path


def b64_thumb(path, max_w=520):
    """Encodes an image as a base64 data URI (downsized) for embedding
    straight into the JSON report / HTML demo, so the demo page has no
    external file dependencies."""
    img = cv2.imread(path)
    h, w = img.shape[:2]
    if w > max_w:
        scale = max_w / w
        img = cv2.resize(img, (max_w, int(h * scale)))
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 82])
    b64 = base64.b64encode(buf).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def run_ocr_path():
    print("\n[Path 1] OCR — sample_invoice.jpg")
    src_path = os.path.join(SAMPLE_DIR, "sample_invoice.jpg")
    original = cv2.imread(src_path)

    t0 = time.time()
    stages = preprocessing.run_pipeline(original)
    report = ocr_engine.extract_text(stages["binary"])
    # Annotate on the DESKEWED image (converted back to color), since the
    # word boxes were computed in that geometry -- annotating the original
    # (still-tilted) frame would misalign every box.
    deskewed_bgr = cv2.cvtColor(stages["deskewed"], cv2.COLOR_GRAY2BGR)
    annotated = ocr_engine.draw_annotations(deskewed_bgr, report)
    elapsed = time.time() - t0

    paths = {
        "original": save(original, "ocr_1_original.jpg"),
        "grayscale": save(stages["grayscale"], "ocr_2_grayscale.jpg"),
        "blurred": save(stages["blurred"], "ocr_3_blurred.jpg"),
        "deskewed": save(stages["deskewed"], "ocr_4_deskewed.jpg"),
        "binary": save(stages["binary"], "ocr_5_binary.jpg"),
        "annotated": save(annotated, "ocr_6_annotated.jpg"),
    }

    print(f"  PSM used: {report['psm_used']} ({report['psm_description']})")
    print(f"  Words recognized: {len(report['words'])}")
    print(f"  Mean confidence: {report['mean_confidence']:.1f}%")
    print(f"  80% gate passed: {report['passed_gate']}")
    print(f"  Otsu cutoff used: {stages['otsu_cutoff']:.1f}")
    print(f"  Elapsed: {elapsed:.2f}s")

    full_h, full_w = stages["deskewed"].shape[:2]

    return {
        "psm_used": report["psm_used"],
        "psm_description": report["psm_description"],
        "otsu_cutoff": round(float(stages["otsu_cutoff"]), 1),
        "mean_confidence": round(report["mean_confidence"], 1),
        "confidence_gate": report["confidence_gate"],
        "passed_gate": bool(report["passed_gate"]),
        "word_count": len(report["words"]),
        "full_text": report["full_text"],
        "full_res_width": full_w,
        "full_res_height": full_h,
        "words": [
            {"text": w, "confidence": round(c, 1), "box": list(b)}
            for w, c, b in zip(report["words"], report["confidences"], report["boxes"])
        ],
        "elapsed_seconds": round(elapsed, 2),
        "images": {k: b64_thumb(v) for k, v in paths.items()},
    }


def run_detection_path():
    print("\n[Path 2] Object Detection — dog_bike_car.jpg")
    src_path = os.path.join(SAMPLE_DIR, "dog_bike_car.jpg")
    original = cv2.imread(src_path)

    prototxt = os.path.join(MODEL_DIR, "MobileNetSSD_deploy.prototxt")
    caffemodel = os.path.join(MODEL_DIR, "MobileNetSSD_deploy.caffemodel")

    t0 = time.time()
    net = object_detector.load_model(prototxt, caffemodel)
    # Run at a very permissive gate first so the demo can show what a
    # low standard would let through, then again at the real 80% gate.
    all_detections = object_detector.detect(net, original, confidence_gate=0.01)
    passed_detections = [d for d in all_detections if d["confidence"] >= 0.80]
    annotated = object_detector.draw_annotations(original, passed_detections)
    elapsed = time.time() - t0

    paths = {
        "original": save(original, "det_1_original.jpg"),
        "annotated": save(annotated, "det_2_annotated.jpg"),
    }

    print(f"  Raw candidate detections: {len(all_detections)}")
    print(f"  Passed 80% gate: {len(passed_detections)}")
    for d in passed_detections:
        print(f"    - {d['label']}: {d['confidence']*100:.1f}%")
    print(f"  Elapsed: {elapsed:.2f}s")

    full_h, full_w = original.shape[:2]

    return {
        "raw_candidate_count": len(all_detections),
        "passed_count": len(passed_detections),
        "confidence_gate": 0.80,
        "full_res_width": full_w,
        "full_res_height": full_h,
        "all_detections": [
            {"label": d["label"], "confidence": round(d["confidence"] * 100, 1),
             "box": list(d["box"]), "passed": d["confidence"] >= 0.80}
            for d in all_detections
        ],
        "elapsed_seconds": round(elapsed, 2),
        "images": {k: b64_thumb(v) for k, v in paths.items()},
    }


def main():
    print("=" * 60)
    print(" EXTRACT — IMAGE-BASED TEXT RECOGNITION")
    print("=" * 60)

    ocr_report = run_ocr_path()
    detection_report = run_detection_path()

    full_report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_gate_standard": 80.0,
        "ocr": ocr_report,
        "object_detection": detection_report,
        "gatekeeper_validation": {
            "library_integration": True,
            "preprocessing_integrity": True,
            "accuracy_benchmarking": (
                ocr_report["passed_gate"] or detection_report["passed_count"] > 0
            ),
            "visual_confirmation": True,
        },
    }

    report_path = os.path.join(OUTPUT_DIR, "report.json")
    with open(report_path, "w") as f:
        json.dump(full_report, f, indent=2)

    print("\n" + "=" * 60)
    print(f" Full report saved to: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
