# Statistics Skill

## File

services/thong_ke_service.py

routes/thong_ke.py

## Purpose

Tổng hợp số liệu nghiệp vụ: lưu lượng xe, doanh thu (UC12, UC13).

## Logic

```text
LuotGuiXe (luotguixe)
        ↓
Lọc theo trạng thái / thời gian
        ↓
Tổng hợp lưu lượng theo giờ
        ↓
Tổng doanh thu (tongphi)
        ↓
Số liệu phân tích cho GenAI
```

## Metrics

```text
tong_luot         tổng số lượt gửi
luu_luong_theo_gio  phân bố theo 24 giờ
tong_doanh_thu    tổng doanh thu (VNĐ)
so_luot_da_tra    số lượt đã trả
so_xe_dang_gui    số xe đang gửi
tong_so_vi_tri    tổng số vị trí
so_ve_thang_hieu_luc  số vé tháng còn hiệu lực
```

## Rules

Doanh thu chỉ tính từ các lượt có `tinhtrang = Đã trả`.

Số liệu thống kê do hệ thống tự tổng hợp, AI không được tự tạo số.

## API

```text
GET /api/thongke/luu-luong?ngay=YYYY-MM-DD
GET /api/thongke/doanh-thu?ngay=YYYY-MM-DD
GET /api/thongke/phan-tich
```

## Core Rule

```text
Statistics aggregates.
GenAI analyzes.
Neither fabricates data.
```
