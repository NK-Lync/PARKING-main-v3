# Parking Visual Debug Skill

## 1. Purpose

Skill này dùng để kiểm tra trực quan kết quả Parking Occupancy Detection.

Mục tiêu:

* Kiểm tra polygon.
* Kiểm tra bounding box.
* Kiểm tra vị trí bottom-center.
* Kiểm tra slot được gán.
* Kiểm tra trạng thái từng slot.

---

## 2. Debug Elements

Ảnh debug nên thể hiện:

```text
Parking Polygon
Vehicle Bounding Box
Vehicle Bottom Center
Slot ID
Slot Name
Slot Status
Vehicle Class
Confidence
```

---

## 3. Vehicle Bounding Box

Format:

```text
[x1, y1, x2, y2]
```

Bounding box được lấy từ:

```text
VehicleDetector
```

---

## 4. Bottom Center

Điểm dùng để xác định slot:

```text
x = (x1 + x2) / 2
y = y2
```

Điểm này nên được vẽ trên ảnh debug.

---

## 5. Polygon

Polygon được chuyển từ normalized coordinates sang pixel coordinates trước khi vẽ.

---

## 6. Slot Assignment

Debug phải cho phép kiểm tra:

```text
Vehicle bbox
      ↓
Bottom center
      ↓
Polygon
      ↓
mavitri
```

Nếu bottom-center nằm trong polygon:

```text
slot = occupied
```

---

## 7. Debug Output

Ví dụ:

```text
Vị trí 5
Trạng thái: Đang sử dụng
Vehicle: car
Confidence: 0.6483
```

---

## 8. Database Safety

Debug visualization chỉ được đọc dữ liệu.

Không được:

* tạo `LuotGuiXe`
* đóng `LuotGuiXe`
* thay đổi `ViTriDo`
* thay đổi `LoaiXe`
* thay đổi `VeThang`

Debug phải độc lập với database mutation.

---

## 9. Purpose

Visual debugging được sử dụng để phát hiện:

* Polygon sai vị trí.
* Polygon chồng lấn.
* Bounding box sai.
* Bottom-center sai.
* Vehicle bị gán nhầm slot.
* Confidence thấp.
* Trạng thái occupancy không chính xác.
