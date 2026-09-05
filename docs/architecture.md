# XeParking Architecture

Tài liệu mô tả kiến trúc và luồng xử lý của hệ thống XeParking.

---

## 1. Tổng quan

XeParking là hệ thống quản lý bãi đỗ xe có tích hợp AI để:

* Nhận diện phương tiện.
* Phát hiện biển số.
* Nhận dạng biển số bằng OCR.
* Phân loại loại xe.
* Xác định vị trí đỗ xe từ hình ảnh.
* Hỗ trợ xe vào, xe ra và đồng bộ trạng thái bãi xe.

Hệ thống được tổ chức theo các tầng:

```text
Client / Camera / Uploaded Image
                │
                ▼
           REST API
             Flask
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
    AI Layer        Business Layer
        │                │
        ▼                │
    AI Flow ─────────────┘
                         │
                         ▼
                  Database Layer
                         │
                         ▼
                Supabase PostgreSQL
```

---

# 2. Project Architecture

Cấu trúc chính của project:

```text
XeParking/
│
├── app.py
│
├── config/
│   └── parking_slots.json
│
├── database/
│   ├── __init__.py
│   └── supabase_client.py
│
├── models/
│   ├── __init__.py
│   ├── loai_xe.py
│   ├── vi_tri_do.py
│   ├── luot_gui_xe.py
│   └── ve_thang.py
│
├── services/
│   ├── __init__.py
│   ├── loai_xe_service.py
│   ├── vi_tri_service.py
│   ├── luot_gui_service.py
│   ├── ve_thang_service.py
│   └── parking_service.py
│
├── ai/
│   ├── __init__.py
│   ├── plate_detector.py
│   ├── plate_recognizer.py
│   ├── vehicle_classifier.py
│   ├── vehicle_detector.py
│   ├── parking_ai_service.py
│   └── parking_occupancy.py
│
└── routes/
    ├── __init__.py
    ├── loai_xe.py
    ├── vi_tri_do.py
    ├── luot_gui_xe.py
    ├── ve_thang.py
    └── parking.py
```

---

# 3. Application Layer

File:

```text
app.py
```

`app.py` là entry point của Flask application.

Nhiệm vụ chính:

* Khởi tạo Flask.
* Cấu hình JSON UTF-8.
* Đăng ký các Blueprint.
* Khởi động REST API.

Các Blueprint hiện tại:

```text
loai_xe_bp
vi_tri_bp
luot_gui_bp
ve_thang_bp
parking_bp
```

---

# 4. API Layer

API layer nằm trong:

```text
routes/
```

API nhận request từ client và chuyển request tới service hoặc AI flow tương ứng.

Các API parking hiện tại:

```text
POST /api/parking/entry
POST /api/parking/exit
GET  /api/parking/status

POST /api/parking/ai-entry
POST /api/parking/ai-exit
POST /api/parking/ai-status
```

Luồng tổng quát:

```text
HTTP Request
     ↓
Flask Route
     ↓
Service / AI Flow
     ↓
Business Processing
     ↓
HTTP Response
```

API không chứa toàn bộ business logic.

---

# 5. AI Layer

AI layer nằm trong:

```text
ai/
```

AI layer chịu trách nhiệm xử lý hình ảnh và tạo ra prediction.

Các thành phần:

```text
VehicleDetector
PlateDetector
PlateRecognizer
VehicleClassifier
ParkingOccupancyDetector
ParkingAIService
```

Nguyên tắc:

```text
Image
 ↓
AI Model
 ↓
Prediction
```

AI prediction sau đó được chuyển tới Business Layer để kiểm tra nghiệp vụ.

---

# 6. Vehicle Detection

File:

```text
ai/vehicle_detector.py
```

Model hiện tại:

```text
YOLO11
yolo11n.pt
```

Các class phương tiện được sử dụng:

```text
2 → car
3 → motorcycle
5 → bus
7 → truck
```

Output gồm:

```text
class_id
class_name
confidence
bbox
```

Luồng:

```text
Image
 ↓
YOLO11
 ↓
Vehicle Detection
 ↓
Bounding Box + Class + Confidence
```

---

# 7. License Plate Detection

File:

```text
ai/plate_detector.py
```

Model hiện tại:

```text
models/license_plate.pt
```

Detector sử dụng YOLO và lọc class:

```text
class_id = 0
```

Các tham số inference hiện tại:

```text
conf = 0.15
imgsz = 1280
iou = 0.45
max_det = 10
```

Luồng:

```text
Image
 ↓
Plate Detector
 ↓
License Plate Bounding Box
```

---

# 8. License Plate Recognition

File:

```text
ai/plate_recognizer.py
```

OCR sử dụng:

```text
EasyOCR
Reader(["en"], gpu=False)
```

Quy trình preprocessing:

```text
Plate Image
     ↓
Grayscale
     ↓
Resize ×2
     ↓
Gaussian Blur
     ↓
EasyOCR
     ↓
Normalize
     ↓
Validate
```

Biển số được chuẩn hóa bằng cách loại bỏ ký tự không phải chữ cái hoặc chữ số.

Format validation hiện tại:

```text
^[0-9]{2}[A-Z][0-9]{4,6}$
```

---

# 9. Vehicle Classification

File:

```text
ai/vehicle_classifier.py
```

Mapping hiện tại:

```text
motorcycle → Xe máy
car        → Ô tô
bus        → Ô tô
truck      → Ô tô
```

Kết quả classification được sử dụng để tìm `maloaixe` tương ứng trong database.

---

# 10. Parking Occupancy

File:

```text
ai/parking_occupancy.py
```

Parking occupancy sử dụng vehicle detection kết hợp với polygon của từng vị trí đỗ.

Cấu hình vị trí:

```text
config/parking_slots.json
```

Quy trình:

```text
Parking Image
      ↓
Vehicle Detection
      ↓
Vehicle Bounding Box
      ↓
Bottom-Center Point
      ↓
Parking Slot Polygon
      ↓
Point-in-Polygon
      ↓
Parking Slot
      ↓
Occupancy Status
```

Bottom-center được tính từ bounding box:

```text
center_x = (x1 + x2) / 2
bottom_y = y2
```

Sau đó sử dụng `cv2.pointPolygonTest()` để xác định điểm đó nằm trong polygon nào.

---

# 11. Parking Slot Configuration

File:

```text
config/parking_slots.json
```

Polygon sử dụng normalized coordinates:

```text
x ∈ [0, 1]
y ∈ [0, 1]
```

Khi xử lý ảnh:

```text
pixel_x = normalized_x × image_width
pixel_y = normalized_y × image_height
```

Mỗi vị trí phải có polygon chứa ít nhất 3 điểm.

Cấu hình hiện tại là layout mẫu 6 vị trí dạng lưới 3×2.

Layout này hiện đang được sử dụng để kiểm thử thuật toán. Khi có ảnh bãi xe thực tế, polygon cần được hiệu chỉnh theo vị trí thực tế trên ảnh.

---

# 12. Parking AI Service

File:

```text
ai/parking_ai_service.py
```

`ParkingAIService` kết hợp các AI component để xử lý một ảnh.

Luồng:

```text
Image
 ↓
Vehicle Detection
 ↓
Vehicle Selection
 ↓
Plate Detection
 ↓
Plate Crop
 ↓
OCR
 ↓
Plate Normalization
 ↓
Vehicle Classification
 ↓
AI Result
```

Service trả về các thông tin chính:

```text
bienso
ocr_confidence
loaixe
vehicle_class
vehicle_confidence
plate_detection_confidence
vehicle_bbox
plate_bbox
```

AI Service tập trung vào việc xử lý và tổng hợp kết quả AI.

Nó không trực tiếp quyết định trạng thái nghiệp vụ của database.

---

# 13. AI Entry Flow

Endpoint:

```text
POST /api/parking/ai-entry
```

Luồng:

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
LoaiXeService
       ↓
ParkingService.vehicle_entry_at_position()
       ↓
LuotGuiXe
       ↓
ViTriDo
```

Trong AI Entry:

1. AI nhận diện biển số.
2. AI xác định loại xe.
3. AI xác định vị trí đỗ.
4. Hệ thống tìm `maloaixe`.
5. `ParkingService` kiểm tra điều kiện nghiệp vụ.
6. Nếu hợp lệ, tạo `LuotGuiXe`.
7. Vị trí được cập nhật thành `"Đang sử dụng"`.

AI không trực tiếp insert `LuotGuiXe`.

---

# 14. AI Exit Flow

Endpoint:

```text
POST /api/parking/ai-exit
```

Luồng:

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
Active LuotGuiXe
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

Phí gửi xe được tính dựa trên:

```text
Thời gian gửi
+
Đơn giá loại xe
+
Trạng thái vé tháng
```

Thời gian gửi được làm tròn theo giờ tính phí.

Thời gian gửi tối thiểu được tính là 1 giờ.

Nếu xe có vé tháng còn hiệu lực:

```text
tongPhi = 0
```

---

# 15. AI Status Flow

Endpoint:

```text
POST /api/parking/ai-status
```

Luồng:

```text
Parking Image
      ↓
ParkingOccupancyDetector
      ↓
AI Occupancy Result
      ↓
ParkingService.sync_ai_occupancy()
      ↓
Compare AI State & Database State
      ↓
Check Active LuotGuiXe
      ↓
Update ViTriDo When Allowed
```

Kết quả đồng bộ được phân loại thành:

```text
updated
overridden
unchanged
failed
```

---

# 16. Business Layer

Business layer nằm trong:

```text
services/
```

Các service:

```text
LoaiXeService
ViTriService
LuotGuiService
VeThangService
ParkingService
```

Trong đó `ParkingService` là service chính cho nghiệp vụ parking.

Business layer chịu trách nhiệm:

* Kiểm tra điều kiện nghiệp vụ.
* Kiểm tra trạng thái xe.
* Kiểm tra vị trí.
* Tạo lượt gửi xe.
* Xử lý xe ra.
* Tính phí.
* Đồng bộ trạng thái vị trí.
* Bảo vệ business truth trước prediction của AI.

---

# 17. Parking Service

File:

```text
services/parking_service.py
```

Các chức năng chính:

```text
vehicle_entry()
vehicle_entry_at_position()
vehicle_exit()
sync_ai_occupancy()
get_status()
```

### Vehicle Entry

```text
Vehicle
 ↓
Validate Plate
 ↓
Validate Vehicle Type
 ↓
Find Available Slot
 ↓
Create LuotGuiXe
 ↓
Update ViTriDo
```

### Vehicle Entry At AI Position

```text
AI Vehicle
 ↓
AI Slot
 ↓
Validate Slot
 ↓
Validate Active Parking
 ↓
Create LuotGuiXe
 ↓
Update ViTriDo
```

### Vehicle Exit

```text
Plate
 ↓
Find Active Parking
 ↓
Calculate Duration
 ↓
Check Monthly Pass
 ↓
Calculate Fee
 ↓
Close Parking
 ↓
Release Slot
```

---

# 18. Database Layer

Database layer sử dụng:

```text
Supabase PostgreSQL
```

Kết nối được thực hiện tại:

```text
database/supabase_client.py
```

Các bảng chính:

```text
loaixe
vitrido
luotguixe
vethang
```

Quan hệ nghiệp vụ:

```text
loaixe
   │
   └──── luotguixe
              │
              └──── vitrido

vethang
   │
   └──── bienso
```

---

# 19. Data Flow

Luồng dữ liệu tổng quát:

```text
                    IMAGE
                      │
                      ▼
                ┌──────────┐
                │ AI Layer │
                └────┬─────┘
                     │
               AI Prediction
                     │
                     ▼
                ┌──────────┐
                │ AI Flow  │
                └────┬─────┘
                     │
              Business Request
                     │
                     ▼
             ┌──────────────┐
             │   Services   │
             └──────┬───────┘
                    │
             Business Validation
                    │
                    ▼
             ┌──────────────┐
             │   Supabase   │
             └──────────────┘
```

---

# 20. AI Prediction vs Business Truth

Đây là nguyên tắc quan trọng của kiến trúc XeParking.

```text
AI Prediction
     ≠
Business Truth
```

AI có thể dự đoán:

```text
Vị trí 2 = Còn trống
```

Nhưng database có thể đang có:

```text
LuotGuiXe
mavitri = 2
tinhtrang = "Đang gửi"
```

Trong trường hợp này:

```text
Active LuotGuiXe
       ↓
Business Truth
       ↓
Không để AI ghi đè thành "Còn trống"
```

`sync_ai_occupancy()` thực hiện nguyên tắc này bằng cách kiểm tra các `LuotGuiXe` đang active trước khi cập nhật `ViTriDo`.

---

# 21. Data Consistency

Hệ thống duy trì các quy tắc chính:

### Một xe không có hai lượt gửi active

```text
Same Plate
    ↓
Active LuotGuiXe exists?
    ↓
Yes → Reject Entry
```

### Một vị trí không có hai xe active

```text
Parking Slot
     ↓
Active LuotGuiXe exists?
     ↓
Yes → Reject Entry
```

Ngoài kiểm tra ở service, hệ thống còn xử lý trường hợp conflict từ unique index:

```text
unique_active_parking_position
```

### Đồng bộ `LuotGuiXe` và `ViTriDo`

Khi xe vào:

```text
LuotGuiXe → Đang gửi
ViTriDo   → Đang sử dụng
```

Khi xe ra:

```text
LuotGuiXe → Đã hoàn tất
ViTriDo   → Còn trống
```

Vị trí chỉ được giải phóng khi không còn `LuotGuiXe` active khác tại vị trí đó.

---

# 22. Separation of Responsibilities

Các tầng có trách nhiệm riêng:

| Layer            | Responsibility                            |
| ---------------- | ----------------------------------------- |
| REST API         | Nhận request và trả response              |
| AI Layer         | Detection, OCR, classification, occupancy |
| AI Flow          | Điều phối nhiều AI component              |
| Business Service | Kiểm tra và thực hiện nghiệp vụ           |
| Database Layer   | Kết nối và lưu dữ liệu                    |
| Supabase         | Lưu business state                        |

Nguyên tắc:

```text
AI → Detect
AI Flow → Orchestrate
Service → Validate & Execute
Database → Store
API → Expose
```

---

# 23. Core Architecture Principle

Kiến trúc XeParking tuân theo nguyên tắc:

```text
AI detects.
AI Flow orchestrates.
Business Service validates.
Database stores business truth.
REST API exposes the result.
```

Không để AI model trực tiếp quyết định hoặc ghi đè business state.

Business logic phải được thực hiện tại Service Layer.

AI prediction được sử dụng như input cho Business Layer.

---

# 24. Current Architecture Limitations

Một số thành phần hiện tại vẫn đang ở mức prototype:

* `parking_slots.json` đang sử dụng layout 6 vị trí dạng lưới mẫu.
* Parking slot polygon chưa được hiệu chỉnh theo ảnh bãi xe thực tế.
* Vehicle/plate association hiện tập trung vào đối tượng được chọn theo confidence trong `ParkingAIService`, chưa phải multi-object tracking hoàn chỉnh.
* `parking-visual-debug` hiện là yêu cầu/debugging approach; chức năng xuất ảnh debug hoàn chỉnh chưa được triển khai thành module riêng.

Các giới hạn này không thay đổi kiến trúc tổng thể của hệ thống.
