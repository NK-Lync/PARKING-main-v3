# Parking Area Skill

## File

services/khu_vuc_service.py

routes/khu_vuc.py

models/khu_vuc.py

## Purpose

Quản lý khu vực đỗ xe và theo dõi sức chứa từng khu vực (UC03).

## Logic

```text
Khu vực (khuvuc)
     ↓
Vị trí đỗ (vitrido) — gắn theo tenkhuvuc
     ↓
Đếm số chỗ trống / số xe hiện tại
     ↓
Báo cáo sức chứa
```

## Fields

```text
makhuvuc     mã khu vực
tenkhuvuc    tên khu vực
tongsovitri  tổng số vị trí
soxehientai  số xe đang gửi hiện tại
```

## Rules

Số chỗ trống được tính từ bảng `vitrido` theo trạng thái `Còn trống`.

Số xe hiện tại được tính từ các lượt gửi active (`tinhtrang = Đang gửi`).

## API

```text
GET    /api/khuvuc
GET    /api/khuvuc/<makhuvuc>
POST   /api/khuvuc
PUT    /api/khuvuc/<makhuvuc>
DELETE /api/khuvuc/<makhuvuc>
GET    /api/khuvuc/cho-trong
POST   /api/khuvuc/cap-nhat
```

## Core Rule

```text
Khu vực là đơn vị tổ chức không gian.
Vị trí là đơn vị nghiệp vụ đỗ xe.
```
