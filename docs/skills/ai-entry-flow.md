# AI Entry Flow Skill

## 1. Purpose

Skill này định nghĩa quy trình cho chức năng cho xe vào bãi bằng hình ảnh AI.

Chức năng được triển khai tại:

```text
POST /api/parking/ai-entry
```

Mục tiêu:

* Nhận ảnh phương tiện.
* Nhận diện phương tiện.
* Nhận diện biển số.
* Đọc biển số bằng OCR.
* Phân loại loại xe.
* Xác định vị trí đỗ bằng AI.
* Kiểm tra tính hợp lệ của dữ liệu nghiệp vụ.
* Tạo lượt gửi xe trong `luotguixe`.
* Cập nhật trạng thái vị trí trong `vitrido`.

---

## 2. Main Modules

### Route

```text
routes/parking.py
```

### AI Service

```text
ai/parking_ai_service.py
```

### Occupancy Detector

```text
ai/parking_occupancy.py
```

### Vehicle Detector

```text
ai/vehicle_detector.py
```

### Plate Detector

```text
ai/plate_detector.py
```

### OCR

```text
ai/plate_recognizer.py
```

### Vehicle Classifier

```text
ai/vehicle_classifier.py
```

### Business Service

```text
services/parking_service.py
```

### Vehicle Type Service

```text
services/loai_xe_service.py
```

---

## 3. Processing Flow

```text
Uploaded Image
      ↓
ParkingAIService.process_image()
      ↓
Vehicle Detection
      ↓
License Plate Detection
      ↓
License Plate OCR
      ↓
Vehicle Classification
      ↓
ParkingOccupancyDetector
      ↓
Determine Parking Slot
      ↓
Validate Vehicle Type
      ↓
Validate License Plate
      ↓
Validate Parking Slot
      ↓
ParkingService.vehicle_entry_at_position()
      ↓
Insert LuotGuiXe
      ↓
Update ViTriDo
```

---

## 4. Input

Request sử dụng `multipart/form-data`.

Field:

```text
image
```

Giá trị là file ảnh.

---

## 5. AI Result

AI service có thể trả về:

```json
{
    "bienso": "60A69696",
    "ocr_confidence": 0.4514,
    "loaixe": "Ô tô",
    "vehicle_class": "car",
    "vehicle_confidence": 0.6483,
    "plate_detection_confidence": 0.4980,
    "vehicle_bbox": [1, 30, 684, 438],
    "plate_bbox": [176, 329, 422, 389]
}
```

---

## 6. Vehicle Type Mapping

AI class được ánh xạ:

```text
motorcycle → Xe máy
car        → Ô tô
bus        → Ô tô
truck      → Ô tô
```

Loại xe sau đó phải được đối chiếu với bảng `loaixe`.

AI không tự quyết định `maloaixe` hoặc `dongia`.

---

## 7. Parking Slot Detection

Vị trí đỗ được xác định bởi:

```text
vehicle bounding box
        ↓
bottom-center point
        ↓
point-in-polygon
        ↓
mavitri
```

Bottom-center:

```text
center_x = (x1 + x2) / 2
center_y = y2
```

---

## 8. Business Validation

Trước khi tạo lượt gửi xe phải kiểm tra:

1. Biển số tồn tại.
2. Biển số không có lượt gửi active.
3. Loại xe tồn tại trong `loaixe`.
4. Vị trí AI xác định tồn tại.
5. Vị trí đang `"Còn trống"`.
6. Vị trí chưa có `LuotGuiXe` active.

Nếu validation thất bại, không tạo lượt gửi xe.

---

## 9. Database Operation

Khi validation thành công:

```text
luotguixe
```

được tạo với:

```text
bienso
maloaixe
mavitri
thoigianvao
tinhtrang = "Đang gửi"
```

Sau đó:

```text
vitrido.trangthai
```

được chuyển thành:

```text
Đang sử dụng
```

---

## 10. Important Rule

AI chỉ xác định:

* xe nào
* biển số nào
* loại xe nào
* vị trí nào

AI không trực tiếp thao tác Supabase.

Business operation phải đi qua:

```text
ParkingService.vehicle_entry_at_position()
```

---

## 11. Failure Cases

Các trường hợp phải từ chối:

```text
Không đọc được ảnh
Không phát hiện xe
Không phát hiện biển số
OCR thất bại
Biển số không hợp lệ
Không tìm thấy loại xe
Không tìm thấy vị trí
Vị trí đã được sử dụng
Xe đã có lượt gửi active
```

---

## 12. Core Principle

```text
AI detects.
Business Service validates.
Database stores business state.
API returns result.
```
