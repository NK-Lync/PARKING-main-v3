# AI Exit Flow Skill

## 1. Purpose

Skill này định nghĩa quy trình cho xe ra bãi bằng hình ảnh AI.

Endpoint:

```text
POST /api/parking/ai-exit
```

Mục tiêu chính:

* Nhận ảnh xe.
* Phát hiện biển số.
* OCR biển số.
* Tìm lượt gửi xe đang active.
* Tính thời gian gửi.
* Kiểm tra vé tháng.
* Tính phí.
* Đóng lượt gửi.
* Giải phóng vị trí.

---

## 2. Main Flow

```text
Uploaded Image
      ↓
Plate Detection
      ↓
Plate OCR
      ↓
Normalize License Plate
      ↓
Find Active LuotGuiXe
      ↓
Calculate Parking Duration
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

## 3. Business Service

Logic xe ra nằm trong:

```text
services/parking_service.py
```

Method:

```text
vehicle_exit(bien_so)
```

Route không tự tính phí.

---

## 4. Find Active Parking

Hệ thống tìm bản ghi:

```text
luotguixe
```

có:

```text
bienso = biển số nhận diện
tinhtrang = "Đang gửi"
```

Nếu không tìm thấy:

```text
ACTIVE_PARKING_NOT_FOUND
```

---

## 5. Parking Duration

Thời gian được tính dựa trên:

```text
thoigianvao
```

và thời điểm xe ra.

Nếu thời gian gửi nhỏ hơn một phút, hệ thống vẫn tính tối thiểu một phút.

Số giờ thanh toán được làm tròn lên.

Tối thiểu:

```text
1 giờ
```

---

## 6. Parking Fee

Nếu xe có vé tháng còn hạn:

```text
tongphi = 0
```

Nếu không có vé tháng hợp lệ:

```text
tongphi = số giờ × đơn giá loại xe
```

Đơn giá lấy từ:

```text
loaixe.dongia
```

AI không tự tạo hoặc tự quyết định giá.

---

## 7. Closing Parking

Sau khi tính phí:

```text
luotguixe.thoigianra
```

được cập nhật.

```text
luotguixe.tongphi
```

được cập nhật.

```text
luotguixe.tinhtrang
```

được chuyển khỏi trạng thái active.

---

## 8. Release Parking Slot

Sau khi xe ra:

```text
vitrido.trangthai
```

được chuyển thành:

```text
Còn trống
```

chỉ khi không còn `LuotGuiXe` active khác sử dụng vị trí đó.

---

## 9. Important Rule

AI chỉ cung cấp biển số.

Business Service chịu trách nhiệm:

* tìm xe
* tính thời gian
* tính phí
* kiểm tra vé tháng
* đóng lượt gửi
* giải phóng vị trí

---

## 10. Core Principle

```text
AI identifies the vehicle.
ParkingService performs the exit transaction.
Database stores the final business state.
```
