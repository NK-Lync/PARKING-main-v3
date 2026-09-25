# Viết lại frontend XeParking — đặc tả thiết kế

Ngày: 26/09/2026
Phạm vi: toàn bộ `frontend/` (HTML, CSS, JS giao diện). Không đụng vào `app.py`,
`routes/`, `services/`, `models/`, database.

## 1. Mục tiêu

Giao diện cũ chạy đúng nhưng trông giống một trang mẫu Bootstrap ghép vội: mọi
màn hình đều là `card` + `table` + `btn btn-primary`, màu sắc và khoảng cách do
Bootstrap quyết định chứ không do ai chọn. Ba thư viện giao diện (Bootstrap,
Bootstrap Icons, Chart.js) đều nạp từ CDN, nên mất mạng là mất luôn giao diện.

Mục tiêu của lần viết lại:

1. Giao diện trông có chủ đích — một hệ thống thiết kế thống nhất, không phải
   các thẻ Bootstrap xếp cạnh nhau.
2. Toàn bộ tài nguyên nằm trong repo. Không gọi ra Internet khi chạy.
3. Không đổi hành vi: mọi endpoint, mọi trường dữ liệu, mọi luồng nghiệp vụ
   giữ nguyên.

## 2. Hướng thẩm mỹ đã chọn

Người dùng chọn **"Dịch vụ công"** — sáng, điềm tĩnh, trang nghiêm kiểu cổng
dịch vụ nhà nước — và bố cục **sidebar xanh dầu đậm**. Ý tưởng: đây là phần mềm
vận hành, nhân viên nhìn suốt ca, nên nền phải sáng và dịu; màu mạnh chỉ dành
cho con số và trạng thái cần chú ý.

Hệ quả cụ thể:

- Nền xám rất nhạt, thẻ trắng, viền mảnh. Không dùng bóng đổ để phân tầng.
- Sidebar xanh dầu đậm, chữ xám xanh nhạt, mục đang mở có vạch sáng bên trái.
- Chữ Be Vietnam Pro — font Việt hoá đầy đủ, dấu tiếng Việt không bị lệch.
- Số liệu dùng `font-variant-numeric: tabular-nums` để các cột số thẳng hàng.

## 3. Hệ thống thiết kế

### 3.1 Màu

Toàn bộ nằm trong `frontend/css/xp.css`, khai báo một lần ở `:root`:

| Token | Giá trị | Dùng cho |
|---|---|---|
| `--xp-bg` | `#f7f8fa` | nền trang |
| `--xp-surface` | `#ffffff` | mặt thẻ |
| `--xp-border` | `#e4e7ec` | viền |
| `--xp-text` / `--xp-muted` | `#101828` / `#667085` | chữ chính / chữ phụ |
| `--xp-side` / `--xp-side-2` | `#0f3a56` / `#0b2c42` | sidebar |
| `--xp-accent` | `#15507a` | nút chính, chỉ số trung tính |
| `--xp-ok` | `#067647` | còn trống, đã trả, vé hiệu lực |
| `--xp-warn` | `#b54708` | đang chiếm chỗ, tỷ lệ lấp đầy cao |
| `--xp-err` | `#b42318` | lỗi, hết chỗ |

Quy ước màu trạng thái, ghi lại để sau này không "sửa nhầm":

- **Xanh = tốt** (chỗ trống, xe đã ra, vé còn hiệu lực).
- **Hổ phách = đang chiếm chỗ** (đang gửi, đang sử dụng, bãi gần đầy).
- **Đỏ chỉ dành cho lỗi.** Cố ý không dùng đỏ cho trạng thái nghiệp vụ.

### 3.2 Chữ

Be Vietnam Pro, bốn mức 400/500/600/700, nhúng sẵn 12 tệp `woff2` (ba bộ ký tự
`vietnamese`, `latin-ext`, `latin`), tổng 216 KB. `frontend/css/fonts.css` do
`_scratch/nhung_font.py` sinh ra, giữ nguyên `unicode-range` gốc.

### 3.3 Bố cục

- `.xp-shell` = sidebar 244px cố định + vùng chính.
- Dưới 992px: sidebar thành ngăn kéo trượt, có nút ba gạch và lớp phủ mờ.
- Dưới 576px: giảm đệm, ẩn tên người dùng ở thanh trên.
- Lưới dùng `auto-fit` + `minmax(min(100%, …))` nên tự dồn cột, không cần
  media query cho từng màn.

## 4. Vì sao gỡ được Bootstrap mà không phải sửa 6 màn CRUD

Đây là điểm mấu chốt của cả lần viết lại.

Trước khi sửa, đã kiểm tra: `bootstrap.Modal` và `bootstrap.Toast` **chỉ** được
gọi trong `ui.js`. Và cả 6 màn CRUD (`khuvuc`, `vitrido`, `loaixe`, `taikhoan`,
`vethang`, `lichsu`) đều dựng bảng qua `App.ui.table()`, 5 màn dựng hộp thoại
qua `App.ui.modal()`.

Nghĩa là: viết lại `ui.js` là tự động nâng cấp cả 6 màn. Cộng thêm các hàm mới
(`card`, `stat`, `field`, `input`, `select`, `confirm`) thì mỗi màn CRUD rút từ
~150 dòng HTML Bootstrap xuống còn ~120 dòng mô tả dữ liệu.

Chi tiết đã làm:

- `App.ui.badge()` nhận cả tên màu Bootstrap cũ (`primary`, `success`…) và ánh
  xạ sang tông mới, nên chỗ nào chưa kịp đổi vẫn hiện đúng màu.
- Giữ nguyên **toàn bộ tên hàm cũ** (`el`, `escape`, `toast`, `fmtMoney`,
  `fmtDateTime`, `badge`, `roleBadge`, `statusBadge`, `boolBadge`, `spinner`,
  `alertLoi`, `table`, `actionButtons`, `modal`, `formButtons`, `addButton`).
  Chỉ thêm hàm mới. Nhờ vậy rủi ro vỡ màn hình giảm mạnh.

## 5. Bản đồ tệp

Thêm mới:

| Tệp | Vai trò |
|---|---|
| `frontend/css/xp.css` | toàn bộ hệ thống thiết kế (~29 KB) |
| `frontend/css/fonts.css` | 12 khai báo `@font-face`, do script sinh |
| `frontend/js/icons.js` | ~45 icon SVG nội tuyến thay Bootstrap Icons |
| `frontend/js/md.js` | chuyển Markdown của AI thành HTML (xem mục 5.1) |
| `frontend/vendor/chart.umd.min.js` | Chart.js 4.4.1 bản UMD |
| `frontend/vendor/fonts/*.woff2` | 12 tệp chữ |

Viết lại: `index.html`, `js/config.js`, `js/ui.js`, `js/router.js`,
`js/charts.js`, `js/camera.js`, và cả 12 màn trong `js/views/`.

Xoá: `frontend/css/styles.css` (238 dòng ghi đè Bootstrap, không còn ai dùng).

### 5.1 Vì sao tự viết bộ chuyển Markdown

Câu trả lời của AI (Gemini, hoặc lớp phân tích nội bộ khi hết hạn mức) là văn bản
Markdown. Trước đây màn Trợ lý AI hiện thẳng văn bản đã thoát ký tự trong một
khối `white-space: pre-wrap`, nên người dùng đọc thấy cả dấu `###`, `**`, `*`
— trông như một tệp thô chứ không phải một câu trả lời.

Không nạp thư viện Markdown từ Internet vì ràng buộc "không gọi ra Internet khi
chạy" ở mục 1. `frontend/js/md.js` chỉ làm đúng những gì văn bản của AI dùng
tới: tiêu đề `#`–`######`, danh sách chấm (`-` `*` `+`) và danh sách số (`1.`),
lồng nhau một mức, `**đậm**`, `*nghiêng*`, `` `mã` ``, bảng, đường kẻ ngang.
Đổi lại phải tự lo một chỗ mà thư viện làm sẵn: **cùng mức thụt lề nhưng khác
kiểu danh sách** (mục `1.` nối tiếp mục `*`) phải đóng danh sách cũ rồi mở
danh sách mới, không thì các mục số bị hiện thành dấu chấm.

**Quy tắc an toàn, không được đảo:** `App.md.render()` thoát ký tự HTML **trước**
khi phân tích, rồi mới chèn thẻ. Nội dung do AI sinh ra là dữ liệu không tin
cậy; đảo thứ tự hai bước đó là mở đường cho nó chèn thẻ vào trang. Không nối
chuỗi chưa thoát vào kết quả.

Trong CSS, khối nhận Markdown thêm lớp `.md` để `white-space` trở lại `normal`
— giữ `pre-wrap` thì mỗi thẻ `<p>`/`<li>` lại đội thêm một dòng trống.

## 6. Những chỗ lệch so với bản mockup — cố ý, xin đừng "sửa lại"

1. **Sơ đồ chỗ đỗ.** Mockup phác V1–V5 là ô tô đặc màu xanh. Bản làm thật thì
   ngược lại: **ô trống = nền trắng viền xanh kèm dấu tích** (xanh nghĩa là
   "đỗ được ở đây"), **ô có xe = nền hổ phách nhạt kèm icon ô tô**. Cách này
   khớp với quy ước màu trạng thái ở mục 3.1 và để dành màu đỏ cho lỗi.

2. **Hai cột màn "xe vào" / "xe ra".** Khối camera cao hơn hẳn khối form, nên
   để tự nhiên thì hai thẻ lệch nhau ~390px. Đã thêm `.xp-split.deu-cao` cho
   hai cột cao bằng nhau.

3. **Nhãn biểu đồ lưu lượng.** Biểu đồ đếm **mọi lượt xe vào đã ghi nhận**,
   không chỉ lượt đã trả, vì `lay_luu_luong()` không lọc theo `tinhtrang`. Đây
   là hành vi có sẵn của backend, không phải lỗi giao diện. Nhãn ghi rõ
   "Tính từ lúc ghi nhận xe vào" để mô tả đúng thứ nó đang đếm.

## 7. Hành vi giữ nguyên có chủ ý

- Lọc lịch sử làm ngay ở client (API trả hết một lần), gõ tới đâu lọc tới đó.
- Không chọn ngày ở màn Thống kê = số liệu **toàn bộ thời gian**, không phải
  hôm nay. Nhãn trên màn hình đổi theo để khỏi hiểu nhầm.
- Sửa tài khoản mà để trống ô mật khẩu = giữ mật khẩu cũ (chỉ gửi trường
  `matkhau` khi người dùng thực sự gõ).
- Không có ngày đăng ký vé tháng thì backend lấy ngày hôm nay.

## 8. Kiểm chứng

Repo **không có test tự động cho giao diện**. Đã kiểm bằng cách mở trình duyệt
thật và đo, không đoán theo ảnh chụp:

- Cả 12 route render không lỗi, bảng có đúng số dòng theo dữ liệu thật.
- Hộp thoại thêm/sửa mở đúng trường, đóng được bằng Esc và bằng nút Huỷ.
- Hộp thoại xác nhận xoá hiện đúng tên bản ghi, bấm Huỷ thì không xoá gì.
- Ở 400px: không tràn ngang ở cả 5 màn đã thử, ngăn kéo mở/đóng đúng.
- Không còn tham chiếu Bootstrap hay CDN nào trong `frontend/` (ngoài phần
  ghi chú trong comment và header giấy phép của chính thư viện Chart.js).

Lưu ý khi tự kiểm: **đổi hash trên thanh địa chỉ không nạp lại trang**, nên sau
khi sửa tệp phải F5 thật thì mới thấy thay đổi.

## 9. Chưa làm

- Chưa có ảnh xem trước khi chia sẻ liên kết (Open Graph). Hiện chỉ có favicon
  SVG nhúng thẳng trong `index.html`.
- Chưa có chế độ nền tối. Bản này cố ý chỉ có một chế độ sáng.
- Biểu đồ chưa có nút tải ảnh hay xuất CSV.
