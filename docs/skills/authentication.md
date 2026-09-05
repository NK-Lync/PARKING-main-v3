# Authentication Skill

## File

services/tai_khoan_service.py

routes/tai_khoan.py

models/tai_khoan.py

## Purpose

Quản lý tài khoản người dùng và xác thực đăng nhập cho hệ thống XeParking (UC01, UC02).

## Roles

Ba vai trò trong hệ thống:

```text
Quản trị viên
Nhân viên bãi xe
Người quản lý
```

## Logic

```text
Tên đăng nhập + Mật khẩu
        ↓
Mã hóa mật khẩu (SHA-256)
        ↓
So khớp với bảng taikhoan
        ↓
Kiểm tra trạng thái tài khoản
        ↓
Trả về vai trò
```

## Password

Mật khẩu KHÔNG được lưu dạng văn bản thuần.

Mật khẩu được mã hóa bằng:

```text
hashlib.sha256
```

## Rules

Tài khoản bị khóa (`trangthai = false`) không được đăng nhập.

Sai tên đăng nhập hoặc sai mật khẩu đều trả về thất bại.

## API

```text
GET    /api/taikhoan
GET    /api/taikhoan/<mand>
POST   /api/taikhoan
PUT    /api/taikhoan/<mand>
DELETE /api/taikhoan/<mand>
POST   /api/taikhoan/dang-nhap
POST   /api/taikhoan/dang-xuat
```

## Core Rule

```text
Authentication belongs to Business Service,
not to AI.
```
