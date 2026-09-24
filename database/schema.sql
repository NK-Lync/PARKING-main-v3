-- ============================================================
-- XeParking - Hệ thống quản lý bãi đỗ xe có tích hợp AI
-- Schema cơ sở dữ liệu (Supabase / PostgreSQL)
-- ============================================================
--
-- File này mô tả ĐẦY ĐỦ 6 bảng tương ứng với các lớp trong
-- mô hình lớp (OOD - tài liệu giai đoạn 4):
--
--   Lớp            →  Bảng
--   -------------------------------
--   TaiKhoan       →  taikhoan
--   KhuVuc         →  khuvuc
--   ViTriDo        →  vitrido
--   LoaiXe         →  loaixe
--   LuotGuiXe      →  luotguixe
--   VeThang        →  vethang
--
-- Ghi chú: hệ thống sử dụng Supabase (PostgreSQL) thông qua
-- REST API (supabase_client.py), KHÔNG dùng MySQL/container
-- chạy local. Toàn bộ dữ liệu lưu trên server trung gian,
-- không phụ thuộc máy local (xem tài liệu giai đoạn 6).
--
-- Cách chạy: mở Supabase → SQL Editor → dán và chạy file này,
-- sau đó chạy file seed.sql để nạp dữ liệu mẫu.
-- ============================================================


-- ============================================================
-- 1. BẢNG LOAIXE (loại phương tiện)
-- ============================================================
CREATE TABLE IF NOT EXISTS loaixe (
    maloaixe      SERIAL PRIMARY KEY,
    tenloaixe     VARCHAR(50)  NOT NULL,
    dongia        NUMERIC(12, 0) NOT NULL,
    CONSTRAINT chk_loaixe_dongia CHECK (dongia > 0)
);

COMMENT ON TABLE loaixe IS 'Loại phương tiện được phép gửi trong bãi';


-- ============================================================
-- 2. BẢNG KHUVUC (khu vực đỗ xe)
-- ============================================================
CREATE TABLE IF NOT EXISTS khuvuc (
    makhuvuc      SERIAL PRIMARY KEY,
    tenkhuvuc     VARCHAR(100) NOT NULL UNIQUE,
    tongsovitri   INTEGER NOT NULL DEFAULT 0,
    soxehientai   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT chk_khuvuc_tongsovitri CHECK (tongsovitri >= 0),
    CONSTRAINT chk_khuvuc_soxehientai CHECK (soxehientai >= 0)
);

COMMENT ON TABLE khuvuc IS 'Khu vực đỗ xe trong bãi';


-- ============================================================
-- 3. BẢNG VITRIDO (vị trí đỗ)
-- ============================================================
-- ViTriDo thuộc về một KhuVuc. Trong phiên bản hiện tại, mối
-- quan hệ được lưu qua tên khu vực (tenkhuvuc) để tương thích
-- với dữ liệu nghiệp vụ đang có (xem chú thích ở cuối file).
-- ============================================================
CREATE TABLE IF NOT EXISTS vitrido (
    mavitri       SERIAL PRIMARY KEY,
    tenkhuvuc     VARCHAR(100) NOT NULL,
    trangthai     VARCHAR(20)  NOT NULL DEFAULT 'Còn trống',
    CONSTRAINT fk_vitrido_khuvuc
        FOREIGN KEY (tenkhuvuc) REFERENCES khuvuc(tenkhuvuc),
    CONSTRAINT chk_vitrido_trangthai
        CHECK (trangthai IN ('Còn trống', 'Đang sử dụng'))
);

COMMENT ON TABLE vitrido IS 'Vị trí đỗ xe trong từng khu vực';


-- ============================================================
-- 4. BẢNG LUOTGUIXE (lượt gửi xe)
-- ============================================================
CREATE TABLE IF NOT EXISTS luotguixe (
    maluotgui     SERIAL PRIMARY KEY,
    bienso        VARCHAR(20)  NOT NULL,
    maloaixe      INTEGER NOT NULL,
    mavitri       INTEGER NOT NULL,
    loaive        VARCHAR(20)  NOT NULL DEFAULT 'VE_LUOT',
    thoigianvao   TIMESTAMP    NOT NULL,
    thoigianra    TIMESTAMP,
    tongphi       NUMERIC(12, 0) NOT NULL DEFAULT 0,
    tinhtrang     VARCHAR(20)  NOT NULL DEFAULT 'Đang gửi',
    CONSTRAINT fk_luotguixe_loaixe
        FOREIGN KEY (maloaixe) REFERENCES loaixe(maloaixe),
    CONSTRAINT fk_luotguixe_vitrido
        FOREIGN KEY (mavitri)  REFERENCES vitrido(mavitri),
    CONSTRAINT chk_luotguixe_loaive
        CHECK (loaive IN ('VE_LUOT', 'VE_THANG')),
    CONSTRAINT chk_luotguixe_tinhtrang
        CHECK (tinhtrang IN ('Đang gửi', 'Đã trả')),
    CONSTRAINT chk_luotguixe_tongphi
        CHECK (tongphi >= 0),
    CONSTRAINT chk_luotguixe_thoigian
        CHECK (thoigianra IS NULL OR thoigianra >= thoigianvao)
);

COMMENT ON TABLE luotguixe IS 'Lượt gửi xe (phiên xe vào → xe ra)';

-- Ràng buộc nghiệp vụ: một vị trí chỉ có tối đa một xe đang gửi.
CREATE UNIQUE INDEX IF NOT EXISTS unique_active_parking_position
    ON luotguixe (mavitri)
    WHERE tinhtrang = 'Đang gửi';

-- Ràng buộc nghiệp vụ: một biển số chỉ có tối đa một lượt đang gửi.
CREATE UNIQUE INDEX IF NOT EXISTS unique_active_parking_plate
    ON luotguixe (bienso)
    WHERE tinhtrang = 'Đang gửi';


-- ============================================================
-- 5. BẢNG VETHANG (vé tháng / khách quen)
-- ============================================================
CREATE TABLE IF NOT EXISTS vethang (
    mave          SERIAL PRIMARY KEY,
    bienso        VARCHAR(20)  NOT NULL,
    tenkhachhang  VARCHAR(100),
    maloaixe      INTEGER,
    ngaydangky    TIMESTAMP,
    ngayhethan    TIMESTAMP    NOT NULL,
    trangthai     BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_vethang_loaixe
        FOREIGN KEY (maloaixe) REFERENCES loaixe(maloaixe)
);

COMMENT ON TABLE vethang IS 'Vé tháng của khách hàng quen';


-- ============================================================
-- 6. BẢNG TAIKHOAN (tài khoản người dùng hệ thống)
-- ============================================================
CREATE TABLE IF NOT EXISTS taikhoan (
    mand          SERIAL PRIMARY KEY,
    tendangnhap   VARCHAR(100) NOT NULL UNIQUE,
    matkhau       VARCHAR(255) NOT NULL,
    vaitro        VARCHAR(50)  NOT NULL,
    trangthai     BOOLEAN      NOT NULL DEFAULT TRUE,
    email         VARCHAR(255),
    sodienthoai   VARCHAR(20),
    CONSTRAINT chk_taikhoan_vaitro
        CHECK (vaitro IN (
            'QUAN_TRI_VIEN',
            'NHAN_VIEN_BAI_XE',
            'NGUOI_QUAN_LY'
        ))
);

COMMENT ON TABLE taikhoan IS 'Tài khoản người dùng hệ thống (đăng nhập và phân quyền)';


-- ============================================================
-- (TÙY CHỌN) Chuẩn hóa vitrido -> khuvuc bằng khóa ngoại makuvuc
-- ============================================================
-- Mô hình lớp OOD dùng maKhuVuc (int) cho quan hệ ViTriDo → KhuVuc.
-- Phiên bản hiện tại giữ tenkhuvuc (chuỗi) để không phá vỡ dữ liệu
-- nghiệp vụ đang có. Nếu muốn chuẩn hóa đúng OOD, bỏ comment:
--
--   ALTER TABLE vitrido
--       ADD COLUMN makuvuc INTEGER REFERENCES khuvuc(makhuvuc);
--
-- rồi cập nhật dữ liệu tương ứng.
-- ============================================================
