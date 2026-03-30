# Face Detection Project (UltraFace - CPU Optimized)

## 🎯 Objective

Implement a **lightweight, real-time human face detection system** that:

* Runs **only on CPU**
* Has **minimal performance impact**
* Works while **gaming and streaming simultaneously**
* Detects **faces only (bounding boxes)** — no landmarks, no pose estimation

---

## ⚙️ Technical Constraints

* Hardware: **Ryzen 9 9950X3D**
* Must avoid high CPU usage (reserve resources for game + stream)
* Real-time processing required
* No GPU dependency

---

## 🧠 Selected Solution

### Model: UltraFace (RFB-320)

* Format: **ONNX**
* Input size: **320x240**
* Size: ~1MB (can be smaller with quantization)
* Designed for **fast CPU inference**

### Why UltraFace

* Extremely lightweight
* Stable real-time performance on CPU
* Simple pipeline (no heavy frameworks)
* Detects **faces only** (exact requirement)

---

## 🏗️ Architecture

```
Webcam → OpenCV → UltraFace (ONNX Runtime) → Face Bounding Boxes → Display
```

* No MediaPipe
* No deep pipeline complexity

---

## 📦 Dependencies

```bash
pip install opencv-python onnxruntime numpy
```

---

## 🔑 Core Implementation Steps

### 1. Load ONNX model

* Use `onnxruntime.InferenceSession`
* CPUExecutionProvider only

### 2. Preprocessing

* Resize frame to **320x240**
* Convert BGR → RGB
* Normalize: `(img - 127) / 128`
* Shape: `(1, 3, H, W)`

### 3. Inference

* Run model with ONNX Runtime
* Outputs:

  * `boxes`
  * `scores`

### 4. Postprocessing

* Filter by confidence threshold (~0.7)
* Convert normalized coords → pixel coords
* Draw bounding boxes

---

## ⚡ Performance Optimizations

### 1. Limit CPU usage (critical)

* Restrict ONNX threads:

```python
intra_op_num_threads = 2
```

---

### 2. Reduce input resolution

```python
frame = cv2.resize(frame, (640, 360))
```

---

### 3. Frame skipping

```python
if frame_id % 2 != 0:
    continue
```

---

### 4. Optional improvements

* Run detection in a **separate thread**
* Use **INT8 quantized model** for lower CPU usage
* Batch processing NOT needed (real-time)

---

## 🚫 Explicit Non-Goals

* No face recognition
* No facial landmarks
* No body / pose detection
* No MediaPipe usage

---

## 🔄 Possible Future Extensions

* Add face tracking (reduce inference frequency)
* Integrate with OBS (overlay)
* Multi-face ID tracking (lightweight tracker)
* Switch to C++ for lower latency

---

## 📌 Current Status

* Model choice finalized (UltraFace)
* Python ONNX pipeline defined
* Optimization strategy identified

---

## ❓ Open Questions for Next Assistant

* Best threading model for zero frame drops?
* Optimal ONNX Runtime settings for Ryzen CPUs?
* Clean way to integrate into OBS (plugin vs window capture)?
* Should tracking (e.g., SORT) be added to reduce CPU further?

---
