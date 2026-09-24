# XeParking — Hệ thống quản lý bãi đỗ xe có tích hợp AI

Backend API (Flask) của hệ thống quản lý bãi đỗ xe tích hợp AI, phục vụ đồ án
**Ứng dụng trí tuệ nhân tạo — Bãi đỗ xe AI** (Nhóm 19).

## Công nghệ chính

| Thành phần | Công nghệ |
|---|---|
| Backend API | Python 3.14 + Flask |
| Cơ sở dữ liệu | **Supabase (PostgreSQL)** qua REST API |
| Nhận diện phương tiện | YOLO11 (Ultralytics) + OpenCV |
| Nhận diện biển số | EasyOCR |
| Phân tích GenAI | OpenAI-compatible `chat/completions` (dự kiến Gemini) |

> **Quyết định cơ sở dữ liệu:** hệ thống dùng Supabase/PostgreSQL trên nền đám mây
> (truy cập qua REST API) thay cho MySQL/container chạy local. Dữ liệu lưu trên server
> trung gian, không phụ thuộc máy local — đã được phê duyệt trong câu hỏi giai đoạn 6.

## Kiến trúc

```
Routes (Flask Blueprint)
    ↓
Services (nghiệp vụ — nguồn sự thật)
    ↓
Database (Supabase / PostgreSQL)
    ↑
AI (phát hiện & đề xuất, không ghi đè nghiệp vụ)
```

- **Routes** (`routes/`): khai báo các Blueprint và API endpoints.
- **Services** (`services/`): chứa toàn bộ quy tắc nghiệp vụ.
- **Database** (`database/`): kết nối Supabase + schema + dữ liệu mẫu.
- **AI** (`ai/`): nhận diện hình ảnh (YOLO11/EasyOCR) và phân tích GenAI.
- **Models** (`models/`): các lớp phản ánh mô hình lớp OOD, tương ứng 1-1 với bảng CSDL.

Nguyên tắc: **AI phát hiện → Service xác thực → Database lưu trữ → API phơi bày.**
Dữ liệu nghiệp vụ (lượt gửi xe, phí, trạng thái vị trí) luôn do tầng Service quản lý;
AI chỉ cung cấp kết quả quan sát/đề xuất.

## Cài đặt

```bash
# 1. Tạo môi trường ảo và kích hoạt (tuỳ chọn)
python -m venv .venv
.venv\Scripts\activate          # Windows

# 2. Cài thư viện
pip install -r requirements.txt
```

## Cấu hình

1. Sao chép file mẫu thành `.env`:
   ```bash
   copy .env.example .env
   ```
2. Điền giá trị thật:
   - `SUPABASE_URL`, `SUPABASE_KEY` — lấy tại Supabase Dashboard → Settings → API.
   - `AI_API_URL`, `AI_API_KEY`, `AI_MODEL_NAME` — dịch vụ GenAI. Dự kiến dùng
     **Gemini** (key lấy tại Google AI Studio) qua endpoint OpenAI-compatible:
     `AI_API_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`,
     `AI_MODEL_NAME=gemini-2.0-flash`. Để trống `AI_API_KEY` để chạy chế độ
     phân tích nội bộ (không cần khóa API).

## Tạo cơ sở dữ liệu

Mở **Supabase → SQL Editor** rồi chạy lần lượt:

1. `database/schema.sql` — tạo 6 bảng + ràng buộc toàn vẹn + index.
2. `database/seed.sql` — nạp dữ liệu mẫu (loại xe, khu vực, vị trí, tài khoản, …).

### Quyền truy cập & RLS (bắt buộc)

Sau khi chạy 2 file trên, mở **SQL Editor** chạy thêm 2 đoạn SQL này để backend
gọi được API (nếu thiếu sẽ gặp lỗi `permission denied` hoặc thấy 0 dòng):

```sql
-- 1) Cấp quyền cho các role
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public
  TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public
  TO anon, authenticated, service_role;

-- 2) Tắt RLS cho 6 bảng (nếu không, role anon chỉ thấy 0 dòng)
ALTER TABLE loaixe    DISABLE ROW LEVEL SECURITY;
ALTER TABLE khuvuc    DISABLE ROW LEVEL SECURITY;
ALTER TABLE vitrido   DISABLE ROW LEVEL SECURITY;
ALTER TABLE luotguixe DISABLE ROW LEVEL SECURITY;
ALTER TABLE vethang   DISABLE ROW LEVEL SECURITY;
ALTER TABLE taikhoan  DISABLE ROW LEVEL SECURITY;
```

> `SUPABASE_KEY` dùng **publishable key** (`sb_publishable_...`). Nếu vẫn bị chặn
> quyền, đổi sang **secret key** (`sb_secret_...`, role `service_role` bỏ qua RLS) —
> lưu ý không đưa secret key lên frontend.

### Tài khoản mẫu

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | Quản trị viên |
| `nhanvien` | `nhanvien123` | Nhân viên bãi xe |
| `quanly` | `quanly123` | Người quản lý |

## Chạy ứng dụng

```bash
python app.py
```

Sau khi chạy, mở trình duyệt tại `http://127.0.0.1:5000` — giao diện web (SPA)
sẽ được hiển thị. Các API REST đều nằm dưới `/api/*`.

## Model AI (vision)

- `yolo11n.pt` — phát hiện phương tiện (Ultralytics, tự tải nếu thiếu).
- `models/license_plate.pt` — **model nhận diện biển số (huấn luyện riêng)**,
  chưa có trong repo (đã bị `.gitignore` loại trừ). Cần huấn luyện hoặc chép vào
  thư mục `models/` để 2 endpoint `/api/parking/ai-entry` và `/api/parking/ai-exit`
  hoạt động.

Model AI được **tải lười (lazy-load)**: app khởi động bình thường kể cả khi thiếu
`license_plate.pt`; chỉ endpoint cần model đó mới báo lỗi khi gọi.

## Một số endpoint chính

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/taikhoan/dang-nhap` | Đăng nhập |
| GET | `/api/parking/trang-thai` | Trạng thái bãi xe |
| POST | `/api/parking/xe-vao` | Xe vào bãi (tự chọn vị trí trống) |
| POST | `/api/parking/xe-vao-vi-tri` | Xe vào tại vị trí AI xác định |
| POST | `/api/parking/xe-ra` | Xe ra khỏi bãi (tính phí) |
| POST | `/api/parking/dong-bo-ai` | Đồng bộ trạng thái vị trí từ AI |
| GET/POST | `/api/loaixe`, `/api/khuvuc`, `/api/vitrido` | Quản lý loại xe, khu vực, vị trí |
| GET/POST | `/api/luotguixe`, `/api/vethang` | Quản lý lượt gửi, vé tháng |
| GET/POST | `/api/taikhoan` | Quản lý tài khoản |
| GET | `/api/thongke/*` | Thống kê |
| POST | `/api/he-thong-ai/*` | Phân tích GenAI |

> Xem chi tiết API trong `docs/skills/api.md`.

## Cấu trúc thư mục

```
PARKING-main v2/
├── app.py                  # Điểm khởi chạy Flask
├── ai/                     # Tầng AI (YOLO11, EasyOCR, GenAI)
├── routes/                 # Blueprint API
├── services/               # Tầng nghiệp vụ
├── models/                 # Lớp mô hình (OOD)
├── database/               # Kết nối Supabase, schema.sql, seed.sql
├── config/                 # Cấu hình vị trí đỗ (parking_slots.json)
├── docs/                   # Tài liệu kiến trúc và skills
├── .env.example            # Mẫu cấu hình môi trường
└── requirements.txt        # Danh sách thư viện
```
