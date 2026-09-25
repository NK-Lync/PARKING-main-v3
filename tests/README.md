# Thư mục kiểm thử

Các script kiểm thử chạy tay, gọi thẳng vào **Supabase thật** và **Gemini thật**.
Không dùng framework nào — chạy trực tiếp bằng Python.

```bash
python tests/test_vong_vao_ra.py
```

Chạy được từ bất kỳ thư mục nào: mỗi file tự thêm gốc dự án vào `sys.path`.

## Cảnh báo: một số file GHI vào database thật

Đây là database đang chứa dữ liệu thật, không phải bản sao. Đọc bảng dưới
trước khi chạy.

| File | Ghi vào DB? | Việc nó làm |
|---|---|---|
| `test_vong_vao_ra.py` | **Có** | Xe vào/ra, tính phí, chọn vị trí, chặn xe vào trùng |
| `test_vong_2.py` | **Có** | 2 partial unique index, tầng bảo vệ nghiệp vụ của AI, quy tắc chọn chỗ |
| `test_http.py` | **Có** | Bật `app.py` rồi gọi API qua HTTP: đăng nhập, vào/ra, danh mục, thống kê |
| `sua_trang_thai_vitrido.py` | **Có** | Sửa chữa: trả 6 vị trí về `'Còn trống'`. Chỉ dùng khi trạng thái bị lệch |
| `test_genai_endpoint.py` | Không | Bật `app.py`, gọi 4 endpoint `/api/ai/*` |
| `test_genai_endpoint_chi_tiet.py` | Không | Như trên, nghỉ 25s giữa các lần gọi, in đầy đủ thông báo lỗi |
| `test_genai_chan_doan.py` | Không | Chẩn đoán: liệt kê model mà key thấy được, gọi thử `chat/completions` |
| `test_genai_ten_model.py` | Không | Dò các tên model Gemini còn sống, tìm tên chạy được |

Ba file ghi dữ liệu đều **tự dọn sạch**: chúng ghi lại `maluotgui` do mình tạo
ra và chỉ xoá đúng những dòng đó, rồi trả trạng thái `vitrido` về như lúc đầu.
Cuối mỗi lần chạy có mục `KET QUA` in ra trạng thái DB để đối chiếu.

> Khi sửa các file này, **đừng** đổi phần dọn sạch sang xoá theo điều kiện tính
> toán lúc chạy (ví dụ `.gt("maluotgui", MAX)`). Nếu biến đó tính ra 0 thì lệnh
> xoá sẽ quét sạch cả bảng. Luôn xoá theo danh sách id cụ thể đã ghi lại.

## Ghi chú

- `test_genai_*`: nếu thấy `nguon='noi-bo'` kèm `canh_bao`, đọc kỹ thông báo —
  hệ thống báo rõ lý do. Lỗi **503 UNAVAILABLE** là Google quá tải tạm thời,
  thử lại sau, **không phải** lỗi cấu hình.
- Endpoint `/api/ai/hoi-dap` nhận trường `cau_hoi` (có gạch dưới), không phải
  `cauhoi`. Gửi sai trả về HTTP 400.
- Các file `test_*.py` ở thư mục gốc dự án là bản cũ, có trước thư mục này.
