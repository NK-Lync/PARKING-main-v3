# XeParking Business Rules Skill

## 1. Purpose

Skill này chứa các quy tắc nghiệp vụ thực tế đang được sử dụng trong XeParking.

---

## 2. Active Parking

Một xe được coi là đang ở trong bãi khi có bản ghi `luotguixe` active với:

```text
tinhtrang = "Đang gửi"
```

---

## 3. One Active Parking Per Vehicle

Một biển số không được đồng thời có nhiều lượt gửi active.

Nếu đã có lượt gửi:

```text
bienso = X
tinhtrang = "Đang gửi"
```

thì không cho xe X vào lần nữa.

---

## 4. One Active Vehicle Per Slot

Một vị trí không được đồng thời chứa nhiều lượt gửi active.

Nếu slot đã có `LuotGuiXe` active:

```text
mavitri = X
```

thì không cho xe khác sử dụng slot đó.

---

## 5. Vehicle Type

Loại xe phải tồn tại trong:

```text
loaixe
```

Không tự tạo loại xe trong quá trình AI xử lý.

---

## 6. Parking Fee

Đơn giá được lấy từ:

```text
loaixe.dongia
```

AI không tự đặt giá.

---

## 7. Monthly Parking

Nếu `vethang` tồn tại và còn hiệu lực:

```text
tongphi = 0
```

Nếu không:

```text
tongphi = parking_duration × dongia
```

---

## 8. AI Is Not Business Truth

AI chỉ cung cấp dự đoán.

AI không được tự ý:

```text
đóng lượt gửi
tính phí
tạo vé tháng
thay đổi lịch sử
```

---

## 9. Database Priority

Trong trường hợp AI mâu thuẫn với dữ liệu nghiệp vụ:

```text
Active LuotGuiXe
        >
AI Occupancy
```

Ví dụ:

```text
AI → slot trống

LuotGuiXe → xe vẫn đang gửi

Kết quả → slot vẫn được coi là đang sử dụng
```

---

## 10. AI Entry

AI phải cung cấp đủ:

```text
bienso
loaixe
mavitri
```

trước khi tạo lượt gửi.

---

## 11. AI Exit

AI cần xác định được biển số.

Business Service mới quyết định:

```text
lượt gửi
thời gian
phí
vé tháng
trạng thái slot
```

---

## 12. Database Consistency

Hai trạng thái phải được duy trì nhất quán:

```text
LuotGuiXe
        ↕
ViTriDo
```

Xe đang gửi phải gắn với một vị trí đang sử dụng.

Xe ra khỏi bãi thì vị trí được giải phóng nếu không còn lượt gửi active khác.

---

## 13. Core Rule

```text
AI predicts.
Business logic decides.
Database persists.
```
