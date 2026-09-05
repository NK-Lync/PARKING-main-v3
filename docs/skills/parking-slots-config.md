# Parking Slots Configuration Skill

## 1. Purpose

Skill này định nghĩa cách cấu hình vị trí đỗ xe cho AI Occupancy Detection.

File:

```text
config/parking_slots.json
```

---

## 2. Configuration Structure

Mỗi parking slot được xác định bằng ID:

```json
{
    "1": {
        "name": "Vị trí 1",
        "polygon": [
            [0.0, 0.0],
            [0.3, 0.0],
            [0.3, 0.5],
            [0.0, 0.5]
        ]
    }
}
```

---

## 3. Slot ID

Key của JSON được chuyển thành:

```text
mavitri
```

Ví dụ:

```text
"5"
```

trở thành:

```python
mavitri = 5
```

---

## 4. Normalized Coordinates

Polygon sử dụng tọa độ normalized.

```text
x ∈ [0, 1]
y ∈ [0, 1]
```

Pixel được tính:

```text
pixel_x = normalized_x × image_width

pixel_y = normalized_y × image_height
```

---

## 5. Polygon Requirement

Mỗi polygon phải có ít nhất 3 điểm.

Nếu polygon có ít hơn 3 điểm:

```text
ValueError
```

---

## 6. Runtime Conversion

`ParkingOccupancyDetector` đọc JSON khi khởi tạo.

Sau đó chuyển polygon normalized sang pixel dựa trên kích thước ảnh thực tế.

Điều này cho phép cùng một cấu hình normalized được áp dụng cho ảnh có kích thước khác nhau.

---

## 7. Important Constraint

Polygon phải mô tả đúng khu vực parking slot thực tế.

Không sử dụng grid giả trong môi trường production.

Grid 3×2 từng được sử dụng chỉ nhằm mục đích kiểm thử thuật toán.

---

## 8. Slot Configuration Rule

Không hard-code polygon trong:

```text
parking_occupancy.py
```

Polygon phải nằm trong:

```text
config/parking_slots.json
```

---

## 9. Relationship

```text
parking_slots.json
        ↓
ParkingOccupancyDetector
        ↓
mavitri
        ↓
ViTriDo.mavitri
```

ID trong configuration phải tương ứng với ID trong database.
