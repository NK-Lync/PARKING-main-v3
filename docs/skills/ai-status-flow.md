# AI Status Flow Skill

## 1. Purpose

Skill này định nghĩa quy trình xác định và đồng bộ trạng thái các vị trí đỗ bằng AI.

Endpoint:

```text
POST /api/parking/ai-status
```

---

## 2. Main Flow

```text
Parking Image
      ↓
VehicleDetector
      ↓
ParkingOccupancyDetector
      ↓
Detect occupied slots
      ↓
Compare with ViTriDo
      ↓
Check active LuotGuiXe
      ↓
sync_ai_occupancy()
      ↓
Update allowed database states
```

---

## 3. Occupancy Detection

AI tạo kết quả:

```text
tong_vi_tri
dang_su_dung
con_trong
ty_le_lap_day
vi_tri
```

Ví dụ:

```json
{
    "tong_vi_tri": 6,
    "dang_su_dung": 1,
    "con_trong": 5,
    "ty_le_lap_day": 16.67
}
```

---

## 4. Slot Result

Mỗi vị trí có:

```json
{
    "mavitri": 5,
    "name": "Vị trí 5",
    "trangthai": "Đang sử dụng",
    "vehicle": {
        "class_name": "car",
        "confidence": 0.6483,
        "bbox": [1, 30, 684, 438]
    }
}
```

---

## 5. Database Synchronization

Method:

```text
ParkingService.sync_ai_occupancy()
```

So sánh:

```text
AI status
    ↕
ViTriDo status
```

đồng thời kiểm tra:

```text
LuotGuiXe active
```

---

## 6. Business Truth Protection

Nếu AI nhận diện:

```text
Còn trống
```

nhưng database có:

```text
LuotGuiXe active
```

thì không được coi vị trí đó là trống.

Ví dụ:

```text
AI:
Vị trí 2 = Còn trống

Database:
Vị trí 2 có LuotGuiXe active

Result:
Vị trí 2 = Đang sử dụng
```

---

## 7. Sync Categories

Kết quả đồng bộ được phân loại:

```text
updated
overridden
unchanged
failed
```

### updated

AI thay đổi trạng thái database hợp lệ.

### overridden

AI đưa ra trạng thái mâu thuẫn với business state và database được bảo vệ.

### unchanged

AI và database đã nhất quán hoặc database đang được bảo vệ bởi lượt gửi active.

### failed

Không thể cập nhật database.

---

## 8. Important Rule

Không sử dụng AI như nguồn dữ liệu nghiệp vụ tuyệt đối.

Thứ tự ưu tiên:

```text
Active LuotGuiXe
        >
AI Occupancy Prediction
```

---

## 9. Core Principle

```text
AI observes parking occupancy.
Business data protects active parking transactions.
Synchronization must never destroy valid business state.
```
