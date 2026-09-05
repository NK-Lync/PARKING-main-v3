# Image Processing Skill

## 1. Purpose

Skill này mô tả các bước xử lý ảnh được sử dụng trong XeParking AI.

---

## 2. Image Loading

Ảnh được nhận từ API dưới dạng uploaded file.

Route lưu ảnh tạm để các AI module xử lý.

---

## 3. Vehicle Detection

`VehicleDetector` nhận đường dẫn ảnh và truyền ảnh vào YOLO.

YOLO trả về:

```text
class
confidence
bounding box
```

---

## 4. Plate Detection

`PlateDetector` sử dụng YOLO license plate model.

Inference sử dụng các tham số hiện tại:

```text
conf = 0.15
imgsz = 1280
iou = 0.45
max_det = 10
```

Các detection có class khác `0` bị bỏ qua.

---

## 5. Plate Cropping

Sau khi phát hiện biển số, ảnh biển số được crop từ bounding box.

Crop có padding bất đối xứng:

```text
left   = 5%
right  = 25%
top    = 15%
bottom = 15%
```

Mục đích là giữ thêm vùng ảnh có thể hữu ích cho OCR.

---

## 6. OCR Preprocessing

Trong `PlateRecognizer`:

```text
BGR Image
    ↓
Grayscale
    ↓
Resize ×2
    ↓
Gaussian Blur
    ↓
EasyOCR
```

---

## 7. OCR

EasyOCR được khởi tạo với:

```python
easyocr.Reader(["en"], gpu=False)
```

OCR trả về:

```text
text
confidence
```

---

## 8. Plate Normalization

OCR text được:

1. Chuyển thành uppercase.
2. Loại bỏ ký tự không phải A-Z hoặc 0-9.
3. Sửa một số lỗi OCR phổ biến.
4. Validate bằng regex.

Ví dụ:

```text
6OA69696
```

được sửa thành:

```text
60A69696
```

---

## 9. Plate Validation

Regex hiện tại:

```text
^[0-9]{2}[A-Z][0-9]{4,6}$
```

Ví dụ hợp lệ:

```text
60A69696
```

Ví dụ có dấu `-` được normalize trước:

```text
60A-696.96
→
60A69696
```

---

## 10. Parking Occupancy

Ảnh parking được xử lý:

```text
Image
 ↓
Vehicle Detection
 ↓
Bounding Box
 ↓
Bottom Center
 ↓
Point-in-Polygon
```

---

## 11. Image Processing Rule

Mọi bước xử lý ảnh phải giữ được:

```text
image dimensions
bounding box coordinates
slot coordinates
```

đồng nhất để tránh gán sai vị trí.
