# XeParking Skills

Tập hợp skill và kiến trúc AI của hệ thống XeParking.

---

## 1. Core AI Skills

Các skill chịu trách nhiệm trực tiếp cho quá trình nhận diện và phân tích hình ảnh:

* `vehicle-detection`
* `license-plate-detection`
* `license-plate-recognition`
* `vehicle-classification`
* `parking-occupancy`

---

## 2. AI Flow Skills

Các skill mô tả quy trình kết hợp nhiều AI module để thực hiện nghiệp vụ:

* `ai-entry-flow`
* `ai-exit-flow`
* `ai-status-flow`

---

## 3. Parking Business Skills

Các skill xử lý nghiệp vụ gửi xe:

* `parking-entry`
* `parking-exit`
* `parking-status-sync`
* `business-rules`

---

## 4. Configuration & Image Skills

Các skill liên quan đến cấu hình vị trí đỗ, xử lý ảnh và kiểm tra trực quan:

* `parking-slots-config`
* `parking-visual-debug`
* `image-processing`
* `model-management`

---

## 5. System & Development Skills

Các skill hỗ trợ tầng hệ thống và phát triển:

* `database-integration`
* `api`
* `debugging`
* `code-review`

---

# 6. System Architecture

XeParking sử dụng kiến trúc trong đó AI chịu trách nhiệm nhận diện, còn Business Service chịu trách nhiệm quyết định nghiệp vụ.

```text
Camera / Uploaded Image
          ↓
   Vehicle Detection
          ↓
 License Plate Detection
          ↓
    License Plate OCR
          ↓
  Vehicle Classification
          ↓
  Parking Occupancy
          ↓
     AI Flow Layer
          ↓
    Parking Service
          ↓
      Supabase
          ↓
       REST API
```

---

# 7. AI Processing Architecture

## Vehicle Detection

```text
Image
 ↓
VehicleDetector
 ↓
YOLO
 ↓
Vehicle Bounding Boxes
```

## License Plate Recognition

```text
Vehicle Image
 ↓
PlateDetector
 ↓
License Plate Bounding Box
 ↓
Image Crop / Preprocessing
 ↓
EasyOCR
 ↓
Normalized License Plate
```

## Vehicle Classification

```text
Vehicle Detection
 ↓
Vehicle Class
 ↓
VehicleClassifier
 ↓
Loại xe
```

Mapping hiện tại:

```text
motorcycle → Xe máy
car        → Ô tô
bus        → Ô tô
truck      → Ô tô
```

---

# 8. Parking Occupancy Architecture

```text
Parking Image
      ↓
Vehicle Detection
      ↓
Vehicle Bounding Box
      ↓
Bottom-Center Point
      ↓
Parking Polygon
      ↓
Point-in-Polygon
      ↓
Parking Slot
      ↓
Occupancy Status
```

Parking polygon được cấu hình trong:

```text
config/parking_slots.json
```

Tọa độ polygon sử dụng normalized coordinates và được chuyển đổi sang pixel coordinates dựa trên kích thước ảnh.

---

# 9. AI Entry Architecture

```text
Uploaded Image
      ↓
ParkingAIService
      ↓
Vehicle Detection
      ↓
Plate Detection
      ↓
OCR
      ↓
Vehicle Classification
      ↓
ParkingOccupancyDetector
      ↓
Determine Parking Slot
      ↓
ParkingService.vehicle_entry_at_position()
      ↓
LuotGuiXe
      ↓
ViTriDo
```

AI không trực tiếp quyết định việc ghi dữ liệu nghiệp vụ.

Business validation được thực hiện bởi `ParkingService`.

---

# 10. AI Exit Architecture

```text
Uploaded Image
      ↓
ParkingAIService
      ↓
Plate Detection
      ↓
OCR
      ↓
License Plate
      ↓
ParkingService.vehicle_exit()
      ↓
Find Active LuotGuiXe
      ↓
Calculate Duration
      ↓
Check VeThang
      ↓
Calculate Fee
      ↓
Close LuotGuiXe
      ↓
Release ViTriDo
```

---

# 11. AI Status Architecture

```text
Parking Image
      ↓
ParkingOccupancyDetector
      ↓
Detect Occupied Slots
      ↓
Compare AI Result with Database
      ↓
Check Active LuotGuiXe
      ↓
sync_ai_occupancy()
      ↓
Update ViTriDo
```

AI status không được phép ghi đè một trạng thái nghiệp vụ hợp lệ.

Nếu một vị trí có `LuotGuiXe` active thì dữ liệu nghiệp vụ được ưu tiên.

---

# 12. Business Layer

Business logic nằm trong:

```text
services/
```

Các service chính:

```text
LoaiXeService
ViTriService
LuotGuiService
VeThangService
ParkingService
```

Đặc biệt:

```text
ParkingService
```

chịu trách nhiệm kiểm tra và thực hiện các nghiệp vụ parking.

---

# 13. Database Layer

Database được sử dụng:

```text
Supabase PostgreSQL
```

Các bảng chính:

```text
loaixe
vitrido
luotguixe
vethang
```

AI không truy cập database trực tiếp để thực hiện nghiệp vụ.

Luồng đúng:

```text
AI
 ↓
AI Service / AI Flow
 ↓
Business Service
 ↓
Supabase
```

---

# 14. API Layer

REST API nằm trong:

```text
routes/
```

Các nhóm API hiện tại:

```text
/api/parking/entry
/api/parking/exit
/api/parking/status
/api/parking/ai-entry
/api/parking/ai-exit
/api/parking/ai-status
```

API là tầng giao tiếp giữa hệ thống bên ngoài và các service bên trong.

---

# 15. Business Truth

Trong trường hợp AI và dữ liệu nghiệp vụ mâu thuẫn:

```text
Active LuotGuiXe
        ↓
Business State
        ↓
AI Prediction
```

Ví dụ:

```text
AI:
Vị trí 2 = Còn trống

Database:
Vị trí 2 có LuotGuiXe active

Result:
Vị trí 2 = Đang sử dụng
```

AI chỉ là nguồn nhận diện, không phải nguồn sự thật nghiệp vụ tuyệt đối.

---

# 16. Error Handling

Các lỗi cần được xử lý ở các tầng tương ứng:

```text
Invalid Image
       ↓
AI Layer

Invalid Detection / OCR
       ↓
AI Service

Invalid Vehicle / Slot / Parking State
       ↓
Business Service

Database Error
       ↓
Database Layer

Invalid Request
       ↓
API Layer
```

---

# 17. Skill Directory

Toàn bộ skill của XeParking được tổ chức như sau:

```text
docs/
│
├── SKILL.md
│
└── skills/
    │
    ├── api.md
    ├── code-review.md
    ├── debugging.md
    │
    ├── vehicle-detection.md
    ├── license-plate-detection.md
    ├── license-plate-recognition.md
    ├── vehicle-classification.md
    ├── parking-occupancy.md
    │
    ├── parking-entry.md
    ├── parking-exit.md
    ├── parking-status-sync.md
    │
    ├── ai-entry-flow.md
    ├── ai-exit-flow.md
    ├── ai-status-flow.md
    │
    ├── parking-slots-config.md
    ├── parking-visual-debug.md
    ├── business-rules.md
    ├── image-processing.md
    └── model-management.md
```

Tổng cộng:

```text
20 Skills
```

---

# 18. Skill Execution Principle

Khi xử lý một yêu cầu liên quan đến hệ thống:

```text
Identify Skill
      ↓
Read Relevant Skill
      ↓
Inspect Existing Implementation
      ↓
Apply Skill Rules
      ↓
Validate Business Rules
      ↓
Update Code if Required
      ↓
Test Result
```

Không tạo implementation mới nếu chức năng tương ứng đã tồn tại trong project.

---

# 19. Core System Principle

XeParking tuân theo nguyên tắc:

```text
AI detects.
AI Skill orchestrates.
Business Service validates.
Database stores business truth.
API exposes result.
```

AI chịu trách nhiệm **nhận diện và phân tích**.

Business Service chịu trách nhiệm **ra quyết định nghiệp vụ**.

Database chịu trách nhiệm **lưu trạng thái nghiệp vụ**.

API chịu trách nhiệm **cung cấp giao diện truy cập hệ thống**.
