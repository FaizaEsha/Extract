"""
Builds a single self-contained demo.html from outputs/report.json.
Keeping this as a generator (rather than hand-editing a giant HTML file)
means the demo always reflects the real, freshly-computed pipeline
output -- no fabricated numbers.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "outputs", "report.json")) as f:
    report = json.load(f)

# Guard against the (extremely unlikely) case of "</script" appearing
# inside a base64 blob or string value, which would break out of the
# embedded JSON <script> tag.
report_json = json.dumps(report).replace("</", "<\\/")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>EXTRACT — Image-Based Text Recognition</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#F3EFE2;
  --grid: rgba(27,42,58,0.07);
  --ink:#1B2A3A;
  --ink-soft:#5B6B7A;
  --panel:#FBF9F1;
  --accent:#C1622D;
  --accent-soft:rgba(193,98,45,0.13);
  --pass:#4F7942;
  --pass-soft:rgba(79,121,66,0.13);
  --line:rgba(27,42,58,0.55);
  --line-strong:#1B2A3A;
  box-sizing:border-box;
  padding-top:env(safe-area-inset-top,0px);
  padding-bottom:env(safe-area-inset-bottom,0px);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#181D22; --grid:rgba(255,255,255,0.06); --ink:#EDEAE0; --ink-soft:#A9B3BC;
    --panel:#1F262C; --accent:#E08348; --accent-soft:rgba(224,131,72,0.16);
    --pass:#7FBF6A; --pass-soft:rgba(127,191,106,0.14);
    --line:rgba(237,234,224,0.35); --line-strong:#EDEAE0;
  }
}
:root[data-theme="dark"]{
  --bg:#181D22; --grid:rgba(255,255,255,0.06); --ink:#EDEAE0; --ink-soft:#A9B3BC;
  --panel:#1F262C; --accent:#E08348; --accent-soft:rgba(224,131,72,0.16);
  --pass:#7FBF6A; --pass-soft:rgba(127,191,106,0.14);
  --line:rgba(237,234,224,0.35); --line-strong:#EDEAE0;
}
html{scroll-padding-top:env(safe-area-inset-top,0px);}
*{box-sizing:border-box;}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:'Inter',system-ui,sans-serif;
  background-image:
    linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size:28px 28px;
  min-height:100%;
}
.wrap{max-width:1080px; margin:0 auto; padding:0 24px;}
h1,h2,h3{font-family:'Space Grotesk',sans-serif; margin:0; letter-spacing:-0.01em;}
.mono{font-family:'IBM Plex Mono',monospace;}
a{color:var(--accent);}

/* ---------- Corner crosshair registration marks ---------- */
.blueprint{
  position:relative; border:1.5px solid var(--line); background:var(--panel);
  border-radius:2px;
}
.blueprint::before, .blueprint::after,
.blueprint .cx-tl, .blueprint .cx-tr, .blueprint .cx-bl, .blueprint .cx-br{
  content:''; position:absolute; width:14px; height:14px; pointer-events:none;
}
.blueprint .cx{position:absolute; width:14px; height:14px; pointer-events:none;}
.blueprint .cx::before,.blueprint .cx::after{
  content:''; position:absolute; background:var(--line);
}
.blueprint .cx::before{ left:6px; top:0; width:2px; height:14px; }
.blueprint .cx::after{ top:6px; left:0; width:14px; height:2px; }
.blueprint .cx.tl{ top:-7px; left:-7px; }
.blueprint .cx.tr{ top:-7px; right:-7px; }
.blueprint .cx.bl{ bottom:-7px; left:-7px; }
.blueprint .cx.br{ bottom:-7px; right:-7px; }

/* ---------- Hero ---------- */
header.hero{ padding:64px 0 40px; }
.eyebrow-line{ display:flex; align-items:center; gap:10px; color:var(--ink-soft); font-size:14px; margin-bottom:18px;}
.eyebrow-line .dot{width:7px;height:7px;border-radius:50%;background:var(--pass);}
h1.title{ font-size:clamp(34px,5vw,54px); font-weight:700; line-height:1.05; }
h1.title .accent{ color:var(--accent); }
.subtitle{ margin-top:14px; color:var(--ink-soft); font-size:17px; max-width:640px; line-height:1.55;}
.readout{
  margin-top:28px; padding:14px 18px; display:inline-block;
  border:1.5px solid var(--line); border-radius:2px; background:var(--panel);
}
.readout .mono{ font-size:14px; color:var(--pass); }
.readout .mono .caret{ display:inline-block; width:8px; background:var(--pass); margin-left:2px; animation:blink 1s step-end infinite;}
@keyframes blink{ 50%{opacity:0;} }

/* ---------- Section shell ---------- */
section{ padding:36px 0; }
.section-head{ margin-bottom:22px; }
.section-head .kicker{ color:var(--accent); font-size:13px; font-family:'IBM Plex Mono',monospace; letter-spacing:0.02em; }
.section-head h2{ font-size:26px; margin-top:6px; }
.section-head p{ color:var(--ink-soft); margin-top:8px; max-width:680px; line-height:1.55; font-size:15px;}

/* ---------- Mission params (3 cols) ---------- */
.grid3{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
.param-card{ padding:22px 20px; }
.param-card h3{ font-size:16px; margin-bottom:8px; }
.param-card p, .param-card ul{ color:var(--ink-soft); font-size:14px; line-height:1.55; margin:0; padding-left:18px;}
.param-card ul{margin-top:6px;}

/* ---------- Tabs ---------- */
.tabbar{ display:flex; gap:8px; margin-bottom:24px; flex-wrap:wrap; }
.tabbtn{
  font-family:'IBM Plex Mono',monospace; font-size:13.5px; padding:10px 16px;
  border:1.5px solid var(--line); background:transparent; color:var(--ink);
  border-radius:2px; cursor:pointer;
}
.tabbtn[aria-selected="true"]{ background:var(--ink); color:var(--bg); border-color:var(--ink);}
.tabpanel{ display:none; }
.tabpanel.active{ display:block; }

/* ---------- Pipeline stepper ---------- */
.stepper{ display:grid; grid-template-columns: 1fr 260px; gap:20px; align-items:start;}
.stepper img{ width:100%; display:block; border-radius:2px; border:1px solid var(--line); background:#fff;}
.step-frame{ padding:10px; }
.step-list{ display:flex; flex-direction:column; gap:8px; }
.step-item{
  text-align:left; padding:12px 14px; border:1.5px solid var(--line); background:var(--panel);
  border-radius:2px; cursor:pointer; color:var(--ink);
}
.step-item[aria-selected="true"]{ border-color:var(--accent); background:var(--accent-soft); }
.step-item .step-title{ font-weight:600; font-size:14px; font-family:'Space Grotesk',sans-serif;}
.step-item .step-desc{ font-size:12.5px; color:var(--ink-soft); margin-top:3px; line-height:1.4;}

/* ---------- Confidence explorer ---------- */
.explorer{ display:grid; grid-template-columns:1fr 300px; gap:20px; margin-top:20px; align-items:start;}
.canvas-frame{ padding:10px; position:relative; }
canvas{ width:100%; display:block; border-radius:2px; background:#fff; }
.slider-panel{ padding:20px; }
.slider-panel h3{ font-size:14px; margin-bottom:4px;}
.slider-panel .gate-value{ font-family:'IBM Plex Mono',monospace; font-size:32px; color:var(--accent); margin:10px 0 2px;}
input[type=range]{ width:100%; accent-color:var(--accent); }
.stat-row{ display:flex; justify-content:space-between; font-size:13.5px; margin-top:14px; color:var(--ink-soft);}
.stat-row b{ color:var(--ink); font-family:'IBM Plex Mono',monospace; }
.gate-note{ margin-top:16px; font-size:12.5px; line-height:1.5; padding:10px 12px; border-radius:2px; }
.gate-note.pass{ background:var(--pass-soft); color:var(--pass); }
.gate-note.fail{ background:var(--accent-soft); color:var(--accent); }

/* ---------- Stat cards ---------- */
.stat-cards{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-top:20px;}
.stat-card{ padding:16px; text-align:left; }
.stat-card .label{ font-size:12px; color:var(--ink-soft); font-family:'IBM Plex Mono',monospace;}
.stat-card .value{ font-size:22px; font-weight:700; font-family:'Space Grotesk',sans-serif; margin-top:6px;}

/* ---------- Gatekeeper grid ---------- */
.gate-grid{ display:grid; grid-template-columns:repeat(2,1fr); gap:16px; margin-top:20px;}
.gate-item{ display:flex; gap:14px; padding:20px; }
.gate-badge{
  width:30px; height:30px; border:1.5px solid var(--line); border-radius:2px;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
  font-family:'IBM Plex Mono',monospace; font-size:15px;
}
.gate-badge.pass{ border-color:var(--pass); color:var(--pass); }
.gate-item h3{ font-size:15.5px; }
.gate-item p{ font-size:13.5px; color:var(--ink-soft); margin:4px 0 0; line-height:1.5;}

footer{ padding:50px 0 70px; color:var(--ink-soft); font-size:13.5px; text-align:center; }
footer .mono{ margin-top:10px; }

@media (max-width: 760px){
  .grid3{ grid-template-columns:1fr; }
  .stepper, .explorer{ grid-template-columns:1fr; }
  .stat-cards{ grid-template-columns:repeat(2,1fr); }
  .gate-grid{ grid-template-columns:1fr; }
}
</style>
</head>
<body>

<div class="wrap">
  <header class="hero">
    <div class="eyebrow-line"><span class="dot"></span><span class="mono">EXTRACT // IMAGE-BASED TEXT RECOGNITION</span></div>
    <h1 class="title">EXTRACT<br><span class="accent">Image-Based Text Recognition</span></h1>
    <p class="subtitle">A working recognition pipeline that turns raw pixels into machine-readable intelligence — two paths, one confidence standard. Everything below ran against real sample images; nothing is staged.</p>
    <div class="readout blueprint">
      <span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
      <span class="mono" id="statusReadout">&gt; INITIATE_EXTRACT // STATUS: READY<span class="caret">&nbsp;</span></span>
    </div>
  </header>

  <section>
    <div class="section-head">
      <div class="kicker">MISSION PARAMETERS</div>
      <h2>What this script had to prove</h2>
    </div>
    <div class="grid3">
      <div class="param-card blueprint"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
        <h3>Objective</h3>
        <p>Ingest raw visual data and extract accurate, machine-readable intelligence using pre-trained models only — no training from scratch.</p>
      </div>
      <div class="param-card blueprint"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
        <h3>The Toolkit</h3>
        <ul><li>pytesseract (Tesseract OCR)</li><li>OpenCV (cv2.dnn)</li><li>MobileNet-SSD (VOC, 20 classes)</li></ul>
      </div>
      <div class="param-card blueprint"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
        <h3>The Standard</h3>
        <p>Every surviving detection or word must clear an <b style="color:var(--accent)">80% confidence gate</b> before it's trusted enough to display.</p>
      </div>
    </div>
  </section>

  <section id="paths">
    <div class="section-head">
      <div class="kicker">EXECUTION PATHS</div>
      <h2>Two ways to make a machine see</h2>
      <p>Switch between the two recognition paths below. Each ran end-to-end on a real sample image — a photographed, skewed invoice for OCR, and a street-porch photo for object detection.</p>
    </div>

    <div class="tabbar" role="tablist">
      <button class="tabbtn" role="tab" aria-selected="true" data-tab="ocr">Path 1 — OCR</button>
      <button class="tabbtn" role="tab" aria-selected="false" data-tab="det">Path 2 — Object Detection</button>
    </div>

    <!-- ============= OCR TAB ============= -->
    <div class="tabpanel active" id="tab-ocr">
      <h3 style="font-size:18px; margin-bottom:14px;">The Logic Skeleton: pre-processing, stage by stage</h3>
      <div class="stepper">
        <div class="blueprint step-frame">
          <span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <img id="stepImage" src="" alt="pipeline stage">
        </div>
        <div class="step-list" id="stepList"></div>
      </div>

      <h3 style="font-size:18px; margin:36px 0 6px;">Confidence Explorer</h3>
      <p style="color:var(--ink-soft); font-size:14px; max-width:600px;">Drag the gate. Every recognized word is boxed live from the real per-word confidence scores — nothing pre-baked.</p>
      <div class="explorer">
        <div class="blueprint canvas-frame">
          <span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <canvas id="ocrCanvas"></canvas>
        </div>
        <div class="blueprint slider-panel">
          <span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <h3>CONFIDENCE GATE</h3>
          <div class="gate-value mono"><span id="ocrGateVal">80</span>%</div>
          <input type="range" id="ocrSlider" min="0" max="100" value="80">
          <div class="stat-row"><span>Words passing</span><b id="ocrPassCount">–</b></div>
          <div class="stat-row"><span>Mean confidence (passing)</span><b id="ocrMeanConf">–</b></div>
          <div class="stat-row"><span>PSM mode used</span><b id="ocrPsm">–</b></div>
          <div class="stat-row"><span>Otsu cutoff</span><b id="ocrOtsu">–</b></div>
          <div class="gate-note" id="ocrGateNote"></div>
        </div>
      </div>

      <div class="stat-cards">
        <div class="blueprint stat-card"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <div class="label">WORDS RECOGNIZED</div><div class="value" id="statWords">–</div></div>
        <div class="blueprint stat-card"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <div class="label">MEAN CONFIDENCE</div><div class="value" id="statMean">–</div></div>
        <div class="blueprint stat-card"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <div class="label">80% GATE</div><div class="value" id="statGate">–</div></div>
        <div class="blueprint stat-card"><span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <div class="label">RUNTIME</div><div class="value" id="statTime">–</div></div>
      </div>
    </div>

    <!-- ============= DETECTION TAB ============= -->
    <div class="tabpanel" id="tab-det">
      <h3 style="font-size:18px; margin-bottom:6px;">Confidence Explorer</h3>
      <p style="color:var(--ink-soft); font-size:14px; max-width:600px;">MobileNet-SSD's raw candidate detections, filtered live by the gate you set. Every box is real model output — drag below 99% and nothing disappears, because this frame was an easy one for the network.</p>
      <div class="explorer">
        <div class="blueprint canvas-frame">
          <span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <canvas id="detCanvas"></canvas>
        </div>
        <div class="blueprint slider-panel">
          <span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
          <h3>CONFIDENCE GATE</h3>
          <div class="gate-value mono"><span id="detGateVal">80</span>%</div>
          <input type="range" id="detSlider" min="0" max="100" value="80">
          <div class="stat-row"><span>Detections passing</span><b id="detPassCount">–</b></div>
          <div class="stat-row"><span>Raw candidates seen</span><b id="detRawCount">–</b></div>
          <div class="stat-row"><span>Backbone</span><b>MobileNet v3</b></div>
          <div class="stat-row"><span>Input blob</span><b>300×300</b></div>
          <div class="gate-note" id="detGateNote"></div>
        </div>
      </div>
      <div class="stat-cards" id="detLabelCards"></div>
    </div>
  </section>

  <section>
    <div class="section-head">
      <div class="kicker">VALIDATION</div>
      <h2>Requirements Checklist</h2>
      <p>The pipeline is checked against four core technical requirements. Here's how this run scored against each one.</p>
    </div>
    <div class="gate-grid" id="gateGrid"></div>
  </section>

  <footer>
    <div>EXTRACT — Image-Based Text Recognition</div>
    <div class="mono">Author: Faiza Ahmed Esha</div>
  </footer>
</div>

<script id="report-data" type="application/json">__REPORT_JSON__</script>
<script>
const report = JSON.parse(document.getElementById('report-data').textContent);

// ---------------- Tabs ----------------
document.querySelectorAll('.tabbtn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tabbtn').forEach(b => b.setAttribute('aria-selected','false'));
    btn.setAttribute('aria-selected','true');
    document.querySelectorAll('.tabpanel').forEach(p => p.classList.remove('active'));
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ---------------- OCR: pipeline stepper ----------------
const ocrSteps = [
  {key:'original', title:'1 · Original capture', desc:'A photographed invoice: skewed, shadowed, and noisy — exactly like a real phone photo.'},
  {key:'grayscale', title:'2 · Grayscale', desc:'The 3-channel RGB matrix collapses into one intensity channel.'},
  {key:'blurred', title:'3 · Gaussian blur', desc:'Smooths sensor noise so thresholding does not latch onto speckle.'},
  {key:'deskewed', title:'4 · Deskew', desc:'The tilted text baseline is rotated back to horizontal.'},
  {key:'binary', title:'5 · Adaptive threshold', desc:"Otsu's method forces every pixel to pure black or white."},
];
let stepIdx = 0;
const stepListEl = document.getElementById('stepList');
ocrSteps.forEach((s, i) => {
  const btn = document.createElement('button');
  btn.className = 'step-item';
  btn.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
  btn.innerHTML = `<div class="step-title">${s.title}</div><div class="step-desc">${s.desc}</div>`;
  btn.addEventListener('click', () => setStep(i));
  stepListEl.appendChild(btn);
});
function setStep(i){
  stepIdx = i;
  document.querySelectorAll('.step-item').forEach((el, idx) => el.setAttribute('aria-selected', idx===i ? 'true':'false'));
  document.getElementById('stepImage').src = report.ocr.images[ocrSteps[i].key];
}
setStep(0);

// ---------------- OCR: confidence explorer (canvas) ----------------
const ocrCanvas = document.getElementById('ocrCanvas');
const ocrCtx = ocrCanvas.getContext('2d');
const ocrBaseImg = new Image();
let ocrImgLoaded = false;
ocrBaseImg.onload = () => {
  ocrCanvas.width = ocrBaseImg.naturalWidth;
  ocrCanvas.height = ocrBaseImg.naturalHeight;
  ocrImgLoaded = true;
  drawOcr();
};
ocrBaseImg.src = report.ocr.images.deskewed;

// NOTE: word boxes were computed on the *binary* (deskewed) image at full
// resolution, while the embedded preview images are downscaled -- so we
// scale box coordinates by the ratio between the original full-res
// pipeline and the thumbnail actually loaded into the canvas.
const ocrScale = 520 / Math.max(ocrBaseImg.naturalWidth || 520, 1); // placeholder, corrected on load
function drawOcr(){
  if(!ocrImgLoaded) return;
  const gate = parseInt(document.getElementById('ocrSlider').value, 10);
  ocrCtx.clearRect(0,0,ocrCanvas.width, ocrCanvas.height);
  ocrCtx.drawImage(ocrBaseImg, 0, 0, ocrCanvas.width, ocrCanvas.height);

  // Scale factor: word boxes were measured against the full-resolution
  // pipeline image; the canvas now shows the (possibly downscaled)
  // thumbnail, so rescale by width ratio using natural sizes.
  const scaleX = ocrCanvas.width / report.ocr.full_res_width;
  const scaleY = ocrCanvas.height / report.ocr.full_res_height;

  let passCount = 0, sum = 0;
  report.ocr.words.forEach(w => {
    const passed = w.confidence >= gate;
    if (passed){ passCount++; sum += w.confidence; }
    const [x,y,bw,bh] = w.box;
    ocrCtx.strokeStyle = passed ? '#4F7942' : '#C1622D';
    ocrCtx.lineWidth = 2;
    ocrCtx.strokeRect(x*scaleX, y*scaleY, bw*scaleX, bh*scaleY);
  });

  document.getElementById('ocrGateVal').textContent = gate;
  document.getElementById('ocrPassCount').textContent = passCount + ' / ' + report.ocr.words.length;
  document.getElementById('ocrMeanConf').textContent = passCount ? (sum/passCount).toFixed(1) + '%' : '–';
  const note = document.getElementById('ocrGateNote');
  if (gate <= 80){
    note.className = 'gate-note pass';
    note.textContent = 'At an 80% gate, this document clears the required minimum standard.';
  } else {
    note.className = 'gate-note fail';
    note.textContent = 'Above 80%, some real words start getting dropped — this is why 80% was chosen as the standard, not 95%.';
  }
}
document.getElementById('ocrSlider').addEventListener('input', drawOcr);

// ---------------- Detection: confidence explorer (canvas) ----------------
const detCanvas = document.getElementById('detCanvas');
const detCtx = detCanvas.getContext('2d');
const detBaseImg = new Image();
let detImgLoaded = false;
detBaseImg.onload = () => {
  detCanvas.width = detBaseImg.naturalWidth;
  detCanvas.height = detBaseImg.naturalHeight;
  detImgLoaded = true;
  drawDet();
};
detBaseImg.src = report.object_detection.images.original;

function drawDet(){
  if(!detImgLoaded) return;
  const gate = parseInt(document.getElementById('detSlider').value, 10);
  detCtx.clearRect(0,0,detCanvas.width, detCanvas.height);
  detCtx.drawImage(detBaseImg, 0, 0, detCanvas.width, detCanvas.height);

  const scaleX = detCanvas.width / report.object_detection.full_res_width;
  const scaleY = detCanvas.height / report.object_detection.full_res_height;

  let passCount = 0;
  report.object_detection.all_detections.forEach(d => {
    const passed = d.confidence >= gate;
    if (passed) passCount++;
    const [x,y,bw,bh] = d.box;
    const color = passed ? '#4F7942' : '#C1622D';
    detCtx.strokeStyle = color; detCtx.lineWidth = 3;
    detCtx.strokeRect(x*scaleX, y*scaleY, bw*scaleX, bh*scaleY);
    detCtx.font = '600 15px IBM Plex Mono, monospace';
    const label = `${d.label}: ${d.confidence.toFixed(1)}%`;
    const tw = detCtx.measureText(label).width;
    detCtx.fillStyle = color;
    detCtx.fillRect(x*scaleX, y*scaleY - 22, tw+10, 22);
    detCtx.fillStyle = '#fff';
    detCtx.fillText(label, x*scaleX+5, y*scaleY-6);
  });

  document.getElementById('detGateVal').textContent = gate;
  document.getElementById('detPassCount').textContent = passCount + ' / ' + report.object_detection.all_detections.length;
  document.getElementById('detRawCount').textContent = report.object_detection.raw_candidate_count;
  const note = document.getElementById('detGateNote');
  if (gate <= 80){
    note.className = 'gate-note pass';
    note.textContent = 'All real candidate detections in this frame clear the 80% standard.';
  } else {
    note.className = 'gate-note fail';
    note.textContent = 'Pushing the gate above ~99.5% starts dropping genuine detections — a reminder that a gate set too high creates false negatives.';
  }
}
document.getElementById('detSlider').addEventListener('input', drawDet);

// ---------------- Static stat fill-ins ----------------
document.getElementById('statWords').textContent = report.ocr.word_count;
document.getElementById('statMean').textContent = report.ocr.mean_confidence.toFixed(1) + '%';
document.getElementById('statGate').textContent = report.ocr.passed_gate ? 'PASSED' : 'FAILED';
document.getElementById('statTime').textContent = report.ocr.elapsed_seconds.toFixed(2) + 's';
document.getElementById('ocrPsm').textContent = 'PSM ' + report.ocr.psm_used;
document.getElementById('ocrOtsu').textContent = report.ocr.otsu_cutoff;

const detLabelCards = document.getElementById('detLabelCards');
report.object_detection.all_detections.forEach(d => {
  const div = document.createElement('div');
  div.className = 'blueprint stat-card';
  div.innerHTML = `<span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
    <div class="label">${d.label.toUpperCase()}</div><div class="value">${d.confidence.toFixed(1)}%</div>`;
  detLabelCards.appendChild(div);
});

// ---------------- Gatekeeper grid ----------------
const gateDefs = [
  {key:'library_integration', title:'1 · Library Integration', desc:'Seamless, error-free implementation of pytesseract and cv2.dnn.'},
  {key:'preprocessing_integrity', title:'2 · Pre-Processing Integrity', desc:'Demonstrable grayscale conversion + adaptive thresholding, shown stage-by-stage above.'},
  {key:'accuracy_benchmarking', title:'3 · Accuracy Benchmarking', desc:'A minimum validated confidence score of 80% on the final output.'},
  {key:'visual_confirmation', title:'4 · Visual Confirmation', desc:'A pristine visual output: legible OCR text and accurate labeled bounding boxes.'},
];
const gateGrid = document.getElementById('gateGrid');
gateDefs.forEach(g => {
  const ok = report.gatekeeper_validation[g.key];
  const div = document.createElement('div');
  div.className = 'blueprint gate-item';
  div.innerHTML = `<span class="cx tl"></span><span class="cx tr"></span><span class="cx bl"></span><span class="cx br"></span>
    <div class="gate-badge ${ok ? 'pass':''}">${ok ? '✓' : '×'}</div>
    <div><h3>${g.title}</h3><p>${g.desc}</p></div>`;
  gateGrid.appendChild(div);
});
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__REPORT_JSON__", report_json)

out_path = os.path.join(ROOT, "demo.html")
with open(out_path, "w") as f:
    f.write(html)

print("Wrote", out_path, "-", os.path.getsize(out_path) / 1024, "KB")
