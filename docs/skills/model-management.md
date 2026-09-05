# AI Model Management Skill

## 1. Purpose

Skill này mô tả cách quản lý các model AI đang được sử dụng trong XeParking.

---

## 2. Vehicle Detection Model

Module:

```text
ai/vehicle_detector.py
```

Model mặc định:

```text
yolo11n.pt
```

Framework:

```text
Ultralytics YOLO
```

---

## 3. Supported Vehicle Classes

YOLO class mapping:

```text
2 → car
3 → motorcycle
5 → bus
7 → truck
```

Các class khác bị bỏ qua.

---

## 4. License Plate Detection Model

Module:

```text
ai/plate_detector.py
```

Model mặc định hiện tại:

```text
models/license_plate.pt
```

Model được sử dụng cho license plate detection.

---

## 5. License Plate Model Output

Model trả về:

```text
class_id
confidence
bbox
```

Chỉ class:

```text
0
```

được coi là:

```text
license_plate
```

---

## 6. OCR Model

OCR sử dụng:

```text
EasyOCR
```

Reader:

```python
easyocr.Reader(["en"], gpu=False)
```

OCR không phải model được quản lý bằng file `.pt` trong project.

---

## 7. Model Loading

Model được load khi class detector được khởi tạo.

Ví dụ:

```python
self.model = YOLO(model_path)
```

---

## 8. Model Path

Model AI không nên được hard-code ở nhiều vị trí.

Vehicle model:

```text
yolo11n.pt
```

License plate model:

```text
models/license_plate.pt
```

---

## 9. Confidence

Mỗi detection phải giữ confidence score.

Vehicle detection:

```text
vehicle_confidence
```

Plate detection:

```text
plate_detection_confidence
```

OCR:

```text
ocr_confidence
```

Confidence được trả về để phục vụ debugging và đánh giá kết quả AI.

---

## 10. Model Output Contract

Vehicle detector:

```json
{
    "class_id": 2,
    "class_name": "car",
    "confidence": 0.6483,
    "bbox": [1, 30, 684, 438]
}
```

Plate detector:

```json
{
    "class_id": 0,
    "class_name": "license_plate",
    "confidence": 0.4980,
    "bbox": [176, 329, 422, 389]
}
```

OCR:

```json
{
    "text": "60A69696",
    "confidence": 0.4514,
    "valid": true
}
```

---

## 11. Model Management Rules

Không thay đổi model trong code business logic.

AI model chỉ chịu trách nhiệm inference.

Business Service không được phụ thuộc trực tiếp vào implementation bên trong model.

---

## 12. Current AI Stack

```text
Ultralytics YOLO
        ↓
Vehicle Detection

Ultralytics YOLO
        ↓
License Plate Detection

EasyOCR
        ↓
License Plate Recognition

OpenCV + NumPy
        ↓
Image Processing + Polygon Geometry
```

---

## 13. Core Principle

```text
Models produce predictions.
AI services interpret predictions.
Business services validate decisions.
```
