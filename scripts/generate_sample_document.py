"""
Generates a synthetic 'scanned invoice' image that mimics real-world OCR
conditions: uneven lighting, slight rotation (skew), and sensor noise.
This gives the pre-processing pipeline (grayscale -> blur -> deskew ->
adaptive threshold) something real to do, and lets us prove each stage
visually — exactly like the 'Logic Skeleton' slide in the project brief.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

random.seed(7)
np.random.seed(7)

W, H = 900, 1150
BASE = (250, 248, 240)

img = Image.new("RGB", (W, H), BASE)
draw = ImageDraw.Draw(img)

font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
mono_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

f_title = ImageFont.truetype(font_path_bold, 40)
f_head = ImageFont.truetype(font_path_bold, 22)
f_body = ImageFont.truetype(font_path_reg, 20)
f_mono = ImageFont.truetype(mono_path, 20)

y = 60
draw.text((60, y), "DECODELABS PVT. LTD.", font=f_title, fill=(20, 20, 20))
y += 55
draw.text((60, y), "Greater Lucknow, India  |  decodelabs.tech@gmail.com", font=f_body, fill=(40, 40, 40))
y += 50
draw.line((60, y, 840, y), fill=(20, 20, 20), width=2)
y += 30

draw.text((60, y), "INVOICE #DL-2026-0042", font=f_head, fill=(20, 20, 20))
y += 40
draw.text((60, y), "Date: 2026-09-18", font=f_body, fill=(20, 20, 20))
y += 30
draw.text((60, y), "Bill To: Vishal Kumar, AI Engineering Intern", font=f_body, fill=(20, 20, 20))
y += 50

headers = ["ITEM", "QTY", "UNIT PRICE", "TOTAL"]
col_x = [60, 500, 620, 760]
for h, x in zip(headers, col_x):
    draw.text((x, y), h, font=f_head, fill=(20, 20, 20))
y += 35
draw.line((60, y, 840, y), fill=(20, 20, 20), width=2)
y += 20

rows = [
    ("Server Rack Unit", "1", "$499.00", "$499.00"),
    ("GPU Compute Module", "2", "$899.00", "$1798.00"),
    ("Cooling Fan Array", "3", "$45.00", "$135.00"),
    ("Network Switch 24-port", "1", "$210.00", "$210.00"),
]
for item, qty, price, total in rows:
    draw.text((col_x[0], y), item, font=f_mono, fill=(30, 30, 30))
    draw.text((col_x[1], y), qty, font=f_mono, fill=(30, 30, 30))
    draw.text((col_x[2], y), price, font=f_mono, fill=(30, 30, 30))
    draw.text((col_x[3], y), total, font=f_mono, fill=(30, 30, 30))
    y += 34

y += 20
draw.line((60, y, 840, y), fill=(20, 20, 20), width=2)
y += 20
draw.text((600, y), "SUBTOTAL:", font=f_head, fill=(20, 20, 20))
draw.text((760, y), "$2642.00", font=f_head, fill=(20, 20, 20))
y += 34
draw.text((600, y), "TAX (8%):", font=f_head, fill=(20, 20, 20))
draw.text((760, y), "$211.36", font=f_head, fill=(20, 20, 20))
y += 34
draw.text((600, y), "TOTAL:", font=f_title, fill=(20, 20, 20))
draw.text((760, y), "$2853.36", font=f_head, fill=(20, 20, 20))

y += 90
draw.text((60, y), "Authorized Signature: ___________________", font=f_body, fill=(20, 20, 20))
y += 40
draw.text((60, y), "Thank you for building the future with DecodeLabs!", font=f_body, fill=(60, 60, 60))

# ---- Corrupt it like a real-world scan/photo ----

# 1. Slight rotation (skew), as flagged in the "Deskewing" slide
img = img.rotate(-3.2, expand=True, fillcolor=BASE, resample=Image.BICUBIC)

# 2. Uneven lighting: a soft radial gradient shadow across the page
w2, h2 = img.size
gradient = Image.new("L", (w2, h2), 0)
gd = ImageDraw.Draw(gradient)
for i in range(0, w2, 4):
    shade = int(60 * (i / w2))
    gd.rectangle((i, 0, i + 4, h2), fill=shade)
gradient = gradient.filter(ImageFilter.GaussianBlur(80))
shadow_layer = Image.new("RGB", img.size, (0, 0, 0))
img = Image.composite(shadow_layer, img, gradient)

# 3. Sensor/chromatic noise
arr = np.array(img).astype(np.int16)
noise = np.random.normal(0, 9, arr.shape).astype(np.int16)
arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)

# 4. Very slight blur, as if from a handheld phone photo
img = img.filter(ImageFilter.GaussianBlur(0.6))

out_path = "/home/claude/project4/sample_images/sample_invoice.jpg"
img.save(out_path, quality=90)
print("Saved:", out_path, img.size)
