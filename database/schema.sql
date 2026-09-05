-- ============================================================
-- XeParking - Schema bổ sung cho các bảng còn thiếu
-- ============================================================
--
-- File này bổ sung các bảng KHUVUC và TAIKHOAN tương ứng
-- với các lớp KhuVuc và TaiKhoan trong mô hình lớp (OOD).
--
-- Lưu ý: chỉ tạo thêm, KHÔNG xóa hay sửa các bảng đã có
-- (loaixe, vitrido, luotguixe, vethang) để tránh ảnh hưởng
-- đến dữ liệu nghiệp vụ hiện tại.
-- ============================================================


-- ------------------------------------------------------------
-- 1. BẢNG KHUVUC (khu vực đỗ xe)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS khuvuc (
    makhuvuc      SERIAL PRIMARY KEY,
    tenkhuvuc     VARCHAR(100) NOT NULL,
    tongsovitri   INTEGER NOT NULL DEFAULT 0,
    soxehientai   INTEGER NOT NULL DEFAULT 0
);


-- ------------------------------------------------------------
-- 2. BẢNG TAIKHOAN (tài khoản người dùng hệ thống)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS taikhoan (
    mand          SERIAL PRIMARY KEY,
    tendangnhap   VARCHAR(100) NOT NULL UNIQUE,
    matkhau       VARCHAR(255) NOT NULL,
    vaitro        VARCHAR(50)  NOT NULL,
    trangthai     BOOLEAN      NOT NULL DEFAULT TRUE,
    email         VARCHAR(255),
    sodienthoai   VARCHAR(20)
);


-- ------------------------------------------------------------
-- 3. (TÙY CHỌN) Liên kết vitrido -> khuvuc bằng khóa ngoại
-- ------------------------------------------------------------
-- Bảng vitrido hiện tại lưu tên khu vực dưới dạng chuỗi
-- tenkhuvuc. Nếu muốn chuẩn hóa thành quan hệ thực sự,
-- bỏ comment dòng dưới và cập nhật dữ liệu:
--
--   ALTER TABLE vitrido
--       ADD COLUMN makuvuc INTEGER REFERENCES khuvuc(makhuvuc);
--
-- Trong phiên bản hiện tại, hệ thống vẫn hoạt động dựa trên
-- tên khu vực (tenkhuvuc) để không làm hỏng dữ liệu đang có.
-- ------------------------------------------------------------
