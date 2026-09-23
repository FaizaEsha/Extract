# 🔎 Extract

**Image-based text and object recognition, validated against an 80% confidence gate.**

## ✨ What it does

- 📄 **OCR** — grayscale → blur → deskew → Otsu threshold, then `pytesseract` reads the cleaned image, auto-selecting the best-scoring page-segmentation mode
- 🎯 **Object detection** — OpenCV's `cv2.dnn` running a pre-trained MobileNet-SSD (20 PASCAL VOC classes)
- 🚦 **80% confidence gate** — anything below the line is dropped, not just displayed dimmer
- 🖼️ **Every pipeline stage saved** to `outputs/`, plus a self-contained `demo.html` for visual inspection

This run scored **89.3% mean OCR confidence** (64 words) and **99.5–99.8% detection confidence** on dog / bicycle / car — full numbers in `outputs/report.json`.

## 🧩 How it works

```
Invoice image → Grayscale → Blur → Deskew → Otsu Threshold → pytesseract → OCR result
Photo         → cv2.dnn + MobileNet-SSD                                  → Detections
                                        ↓
                          80% Confidence Gate → outputs/ + report.json
```

## 🛠️ Tech stack

| Layer            | Tools                                               |
| ----------------- | ---------------------------------------------------- |
| OCR               | Python, `pytesseract`                                |
| Object detection  | OpenCV `cv2.dnn`, pre-trained MobileNet-SSD           |
| Pre-processing    | OpenCV — grayscale, Gaussian blur, deskew, Otsu threshold |

## 📂 Project structure

```
extract/
├── src/
│   ├── preprocessing.py      # pre-processing pipeline
│   ├── ocr_engine.py         # OCR path
│   ├── object_detector.py    # detection path
│   └── main.py                # runs both paths, writes outputs/ + report.json
├── models/                    # MobileNet-SSD weights
├── sample_images/
├── scripts/
├── outputs/                   # generated: pipeline stages + report.json
├── demo.html
├── requirements.txt
└── README.md
```

## 🚀 Getting started

```
git clone https://github.com/FaizaEsha/extract.git
cd extract
pip install -r requirements.txt

# Tesseract's binary isn't a Python package — install it separately:
#   Windows: https://github.com/UB-Mannheim/tesseract/wiki
#   macOS:   brew install tesseract
#   Linux:   sudo apt-get install tesseract-ocr

python3 src/main.py                 # runs both paths
python3 scripts/generate_demo.py    # rebuilds demo.html
```

Open `demo.html` in any browser — fully self-contained, works offline.

## 🌱 About

Built as Project 4 (Image or Text Recognition — Basic) for the DecodeLabs AI Engineering Internship.

## ✍️ Author

**Faiza Ahmed Esha**
