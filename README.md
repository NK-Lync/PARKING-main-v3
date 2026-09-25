# XeParking — Hệ thống quản lý bãi đỗ xe có tích hợp AI

Backend API (Flask) của hệ thống quản lý bãi đỗ xe tích hợp AI, phục vụ đồ án
**Ứng dụng trí tuệ nhân tạo — Bãi đỗ xe AI** (Nhóm 19).

## Công nghệ chính

| Thành phần | Công nghệ |
|---|---|
| Backend API | Python 3.14 + Flask |
| Cơ sở dữ liệu | **Supabase (PostgreSQL)** qua REST API |
| Nhận diện phương tiện | YOLO11 (Ultralytics) + OpenCV |
| Nhận diện biển số | YOLO11 (model tự huấn luyện) + EasyOCR |
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

Có hai luồng tuỳ bạn là ai. **Cả hai đều dùng chung một script `setup`** — script
tự nhận biết đang chạy ở luồng nào.

### Dành cho người tải bản public

```bash
git clone https://github.com/NK-Lync/PARKING-main-v2.git
cd "PARKING-main-v2"
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

**macOS / Linux:**
```bash
bash setup.sh
```

Script tạo `venv`, cài thư viện, và tạo `.env` từ file mẫu. Sau đó bạn **tự tạo một
Supabase project riêng** và điền credentials — xem [Cấu hình](#cấu-hình) và
[Tạo cơ sở dữ liệu](#tạo-cơ-sở-dữ-liệu).

> **Repo này không kèm credentials.** Đó là chủ ý: bạn đọc được **toàn bộ** code,
> nhưng phải tự dựng database của mình để chạy. Xem
> [Chạy thử không cần credentials của tác giả](#chạy-thử-không-cần-credentials-của-tác-giả)
> để biết cách làm trong ~5 phút.

### Dành cho người trong nhóm

Nhóm dùng thêm một repo private chứa `.env` thật và model tự huấn luyện:

```bash
git clone https://github.com/NK-Lync/PARKING-main-v2.git
cd "PARKING-main-v2"
git clone https://github.com/NK-Lync/PARKING-main-v2-private.git _private
```

Rồi chạy `setup.ps1` / `setup.sh` như trên. Script tự phát hiện `_private/`, copy
`.env` và model sang — không cần cấu hình tay, không cần liên hệ ai để xin key.

Thư mục `_private/` đã nằm trong `.gitignore` nên **không bao giờ** bị commit ngược
lên repo public.

## Cấu hình

1. Sao chép file mẫu thành `.env` (script `setup` đã tự làm bước này):
   ```bash
   copy .env.example .env
   ```
2. Điền giá trị thật:
   - `SUPABASE_URL` — dạng `https://<project-ref>.supabase.co`. Lưu ý **không** dán
     URL trên thanh địa chỉ dashboard (`supabase.com/dashboard/project/...`), backend
     sẽ không kết nối được.
   - `SUPABASE_KEY` — publishable key, lấy tại Supabase Dashboard → Settings → API.
   - `AI_API_URL`, `AI_API_KEY`, `AI_MODEL_NAME` — dịch vụ GenAI. Dự kiến dùng
     **Gemini** (key lấy tại Google AI Studio) qua endpoint OpenAI-compatible:
     `AI_API_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`,
     `AI_MODEL_NAME=gemini-3.1-flash-lite`. Để trống `AI_API_KEY` để chạy chế độ
     phân tích nội bộ (không cần khóa API).

> Nếu đã điền `AI_API_KEY` mà phản hồi vẫn có `"nguon": "noi-bo"`, kiểm tra trường
> `canh_bao` trong cùng phản hồi — hệ thống báo rõ lý do không gọi được GenAI.

## Tạo cơ sở dữ liệu

### Trường hợp 1 — Project Supabase mới (chưa có gì)

Mở **Supabase → SQL Editor** rồi chạy lần lượt:

1. `database/schema.sql` — tạo 6 bảng + ràng buộc toàn vẹn + index.
2. `database/seed.sql` — nạp dữ liệu mẫu (loại xe, khu vực, vị trí, tài khoản, …).
3. `database/quyen_truy_cap.sql` — cấp quyền và tắt RLS cho backend.

### Trường hợp 2 — Database đã có dữ liệu từ bản cũ

Bản cũ lưu khu vực của vị trí đỗ dưới dạng **chuỗi tên** (`vitrido.tenkhuvuc`).
Bản hiện tại dùng **khóa ngoại** (`vitrido.makhuvuc` → `khuvuc.makhuvuc`), khớp với
mô hình lớp OOD.

`database/schema.sql` dùng `CREATE TABLE IF NOT EXISTS`, nên chạy nó trên database
đã tồn tại sẽ **không thay đổi gì** — bảng `vitrido` vẫn giữ cột cũ, và `seed.sql`
sau đó sẽ báo lỗi. Phải chạy migration riêng:

1. `database/migrate_khuvuc.sql` — chuyển `tenkhuvuc` sang `makhuvuc`, có sao lưu
   và chốt an toàn (tự hủy nếu dữ liệu không khớp khu vực).
2. `database/quyen_truy_cap.sql` — cấp quyền và tắt RLS cho backend.

> **`seed.sql` xóa sạch dữ liệu.** File này mở đầu bằng `TRUNCATE ... RESTART
> IDENTITY` trên cả 6 bảng, tức là **xóa toàn bộ dữ liệu đang có** rồi nạp lại
> dữ liệu mẫu. Nếu database đang chứa dữ liệu thật (lượt gửi, vé tháng, tài
> khoản đã tạo), **đừng chạy seed.sql** — chỉ chạy `migrate_khuvuc.sql` và
> `quyen_truy_cap.sql`. Nếu vẫn muốn nạp dữ liệu mẫu, sao lưu trước bằng
> Supabase → Database → Backups.

### Quyền truy cập & RLS (bắt buộc)

Sau khi chạy schema/seed, mở **SQL Editor** và chạy file
`database/quyen_truy_cap.sql`. File này cấp quyền cho các role và tắt RLS cho 6
bảng — thiếu bước này backend sẽ gặp `permission denied` hoặc đọc ra 0 dòng dù
bảng đã có dữ liệu.

> **Cảnh báo.** Cách này mở toàn quyền đọc/ghi/xóa cho role `anon` — ai có
> publishable key đều thao tác được dữ liệu, không cần đăng nhập. Đây là lựa chọn
> cho đồ án chạy demo, **không dùng cho hệ thống thật**. Vì vậy tuyệt đối không
> commit key thật lên repo public.

> `SUPABASE_KEY` dùng **publishable key** (`sb_publishable_...`). Nếu vẫn bị chặn
> quyền, đổi sang **secret key** (`sb_secret_...`, role `service_role` bỏ qua RLS) —
> lưu ý không đưa secret key lên frontend.

### Tài khoản mẫu

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | Quản trị viên |
| `nhanvien` | `nhanvien123` | Nhân viên bãi xe |
| `quanly` | `quanly123` | Người quản lý |

## Chạy thử không cần credentials của tác giả

Bạn **không cần** xin key của nhóm để chạy thử toàn bộ hệ thống. Cách làm:

1. Tạo một project Supabase miễn phí tại https://supabase.com (~2 phút).
2. Mở **SQL Editor**, chạy lần lượt `database/schema.sql` rồi `database/seed.sql`.
3. Chạy tiếp `database/quyen_truy_cap.sql`.
4. Điền `SUPABASE_URL` và `SUPABASE_KEY` của project đó vào `.env`.
5. Chạy app rồi đăng nhập bằng [tài khoản mẫu](#tài-khoản-mẫu).

GenAI là tuỳ chọn — để trống `AI_API_KEY` thì hệ thống tự chạy chế độ phân tích
nội bộ, không cần khóa API.

## Chạy ứng dụng

```bash
# Windows
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

python app.py
```

Sau khi chạy, mở trình duyệt tại `http://127.0.0.1:5000` — giao diện web (SPA)
sẽ được hiển thị. Các API REST đều nằm dưới `/api/*`.

Biến môi trường khi chạy `python app.py`:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `HOST` | `127.0.0.1` | Đổi thành `0.0.0.0` để máy khác trong LAN truy cập được |
| `PORT` | `5000` | Cổng lắng nghe |
| `FLASK_DEBUG` | tắt | Đặt `1` để bật debug — **không bật khi đã deploy** |

## Triển khai (deploy)

Backend là một Flask app thuần, không phụ thuộc trạng thái local, nên deploy được
lên bất kỳ nền tảng chạy Python nào (Render, Railway, Fly.io, VPS…).

**Lệnh chạy production:**

```bash
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

Lưu ý khi deploy:

- `gunicorn` đã có trong `requirements.txt`.
- Khai báo đủ 5 biến môi trường (`SUPABASE_URL`, `SUPABASE_KEY`, `AI_API_URL`,
  `AI_API_KEY`, `AI_MODEL_NAME`) trong phần Environment của nền tảng — **không**
  dựa vào file `.env` vì file đó không được commit.
- Nền tảng tự gán `PORT`; `gunicorn` ở trên đọc biến đó.
- Cảnh báo ở mục RLS càng đúng khi đã lên internet: đặt secret thật, và cân nhắc
  bật lại RLS kèm policy trước khi cho người ngoài dùng.

## Model AI (vision)

- `yolo11n.pt` — phát hiện phương tiện (Ultralytics, tự tải nếu thiếu).
- `models/license_plate.pt` — **model nhận diện biển số (huấn luyện riêng)**.
  Không có trong repo public (đã bị `.gitignore` loại trừ).

  Model có **2 lớp**: `BSD` (biển dài 1 dòng) và `BSV` (biển vuông 2 dòng) —
  cả hai đều được nhận. Cần có file này để 2 endpoint `/api/parking/ai-entry` và
  `/api/parking/ai-exit` hoạt động.

> Người trong nhóm: `license_plate.pt` nằm trong repo private, `setup.ps1` /
> `setup.sh` sẽ tự copy sang. Không cần tải tay.

Model AI được **tải lười (lazy-load)**: app khởi động bình thường kể cả khi thiếu
`license_plate.pt`; chỉ endpoint cần model đó mới báo lỗi khi gọi.

### Huấn luyện lại model biển số

```bash
python train_plate.py --data archive/dataset.yaml
```

Trọng số tốt nhất được chép vào `models/license_plate.pt`. Các tham số khác:
`--epochs`, `--imgsz`, `--batch`, `--device`, `--name`, `--output`.

> Thư mục `archive/` kèm theo dự án **không huấn luyện lại được**: chỉ có ảnh
> `.png`, thiếu toàn bộ file nhãn `.txt` và thiếu `images/val/` mà `dataset.yaml`
> trỏ tới. Muốn huấn luyện lại phải chuẩn bị bộ dữ liệu có nhãn đầy đủ.

## Một số endpoint chính

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/taikhoan/dang-nhap` | Đăng nhập |
| POST | `/api/taikhoan/dang-xuat` | Đăng xuất |
| GET | `/api/parking/status` | Trạng thái bãi xe (tổng/trống/đang dùng, danh sách xe) |
| POST | `/api/parking/entry` | Xe vào bãi (tự chọn vị trí trống) |
| POST | `/api/parking/exit` | Xe ra khỏi bãi (tính phí) |
| POST | `/api/parking/ai-entry` | Xe vào bằng ảnh — AI nhận biển số + vị trí |
| POST | `/api/parking/ai-exit` | Xe ra bằng ảnh |
| POST | `/api/parking/ai-status` | AI quan sát → đồng bộ trạng thái vị trí |
| GET/POST | `/api/khuvuc` | Quản lý khu vực |
| GET | `/api/khuvuc/cho-trong` | Số chỗ trống theo từng khu vực |
| POST | `/api/khuvuc/cap-nhat` | Đồng bộ `soxehientai` của các khu vực |
| GET/POST | `/api/vitrido` | Quản lý vị trí đỗ |
| GET/POST | `/api/loaixe` | Quản lý loại xe |
| GET/POST | `/api/luotguixe` | Quản lý lượt gửi xe |
| GET/POST | `/api/vethang` | Quản lý vé tháng |
| GET/POST | `/api/taikhoan` | Quản lý tài khoản |
| GET | `/api/thongke/luu-luong` | Thống kê lưu lượng |
| GET | `/api/thongke/doanh-thu` | Thống kê doanh thu |
| GET | `/api/thongke/phan-tich` | Dữ liệu tổng hợp cho phân tích |
| POST | `/api/ai/bao-cao-luu-luong` | GenAI: báo cáo lưu lượng |
| POST | `/api/ai/gio-cao-diem` | GenAI: phân tích giờ cao điểm |
| POST | `/api/ai/goi-y-nhan-su` | GenAI: gợi ý bố trí nhân sự |
| POST | `/api/ai/hoi-dap` | GenAI: hỏi đáp dữ liệu |

Các endpoint `/api/khuvuc/<id>`, `/api/vitrido/<id>`, `/api/loaixe/<id>`,
`/api/luotguixe/<id>`, `/api/vethang/<id>`, `/api/taikhoan/<id>` đều hỗ trợ
GET / PUT / DELETE cho một bản ghi.

> Xem chi tiết API trong `docs/skills/api.md`.

## Cấu trúc thư mục

```
PARKING-main v3/
├── app.py                  # Điểm khởi chạy Flask
├── setup.ps1               # Chuẩn bị môi trường (Windows)
├── setup.sh                # Chuẩn bị môi trường (macOS / Linux)
├── train_plate.py          # Huấn luyện model biển số
├── ai/                     # Tầng AI (YOLO11, EasyOCR, GenAI)
├── routes/                 # Blueprint API
├── services/               # Tầng nghiệp vụ
├── models/                 # Lớp mô hình (OOD) + model .pt
├── database/               # Kết nối Supabase, schema.sql, seed.sql,
│                           #   quyen_truy_cap.sql, migrate_khuvuc.sql
├── config/                 # Cấu hình vị trí đỗ (parking_slots.json)
├── docs/                   # Tài liệu kiến trúc và skills
├── .env.example            # Mẫu cấu hình môi trường
└── requirements.txt        # Danh sách thư viện

_private/                   # (tuỳ chọn) clone repo private — .env thật + model
                            #  Đã nằm trong .gitignore, không bao giờ bị commit
```
