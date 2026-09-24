-- ============================================================
-- XeParking - Dữ liệu mẫu (seed data)
-- Supabase / PostgreSQL
-- ============================================================
--
-- Chạy SAU database/schema.sql (tạo bảng xong mới nạp dữ liệu).
-- Script an toàn khi chạy lại nhiều lần: xóa dữ liệu cũ rồi
-- nạp lại từ đầu (TRUNCATE ... RESTART IDENTITY).
-- ============================================================

-- Xóa dữ liệu cũ (theo thứ tự an toàn khóa ngoại, reset SERIAL về 1)
TRUNCATE TABLE
    luotguixe,
    vethang,
    vitrido,
    khuvuc,
    loaixe,
    taikhoan
RESTART IDENTITY CASCADE;


-- ============================================================
-- 1. LOAIXE (loại phương tiện)
-- ============================================================
INSERT INTO loaixe (tenloaixe, dongia) VALUES
    ('Xe máy', 5000),
    ('Ô tô',   20000);


-- ============================================================
-- 2. KHUVUC (khu vực đỗ)
-- ============================================================
INSERT INTO khuvuc (tenkhuvuc, tongsovitri, soxehientai) VALUES
    ('Khu A', 3, 0),
    ('Khu B', 3, 0);


-- ============================================================
-- 3. VITRIDO (vị trí đỗ)
--    6 vị trí, khớp với config/parking_slots.json (lưới 3×2).
--    Vị trí 1-3 thuộc Khu A, vị trí 4-6 thuộc Khu B.
-- ============================================================
INSERT INTO vitrido (tenkhuvuc, trangthai) VALUES
    ('Khu A', 'Còn trống'),  -- mavitri = 1
    ('Khu A', 'Còn trống'),  -- mavitri = 2
    ('Khu A', 'Còn trống'),  -- mavitri = 3
    ('Khu B', 'Còn trống'),  -- mavitri = 4
    ('Khu B', 'Còn trống'),  -- mavitri = 5
    ('Khu B', 'Còn trống');  -- mavitri = 6


-- ============================================================
-- 4. VETHANG (vé tháng mẫu)
-- ============================================================
INSERT INTO vethang (
    bienso,
    tenkhachhang,
    maloaixe,
    ngaydangky,
    ngayhethan,
    trangthai
) VALUES
    ('30A-12345', 'Nguyễn Văn A', 2, '2026-09-01 08:00:00', '2026-12-31 23:59:59', TRUE);


-- ============================================================
-- 5. TAIKHOAN (tài khoản mẫu)
--    Mật khẩu lưu dạng SHA-256 (khớp TaiKhoanService._ma_hoa_mat_khau)
--
--    admin123    → QUAN_TRI_VIEN     (Quản trị viên)
--    nhanvien123 → NHAN_VIEN_BAI_XE  (Nhân viên bãi xe)
--    quanly123   → NGUOI_QUAN_LY     (Người quản lý)
-- ============================================================
INSERT INTO taikhoan (
    tendangnhap,
    matkhau,
    vaitro,
    trangthai,
    email,
    sodienthoai
) VALUES
    (
        'admin',
        '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        'QUAN_TRI_VIEN',
        TRUE,
        'admin@xeparking.vn',
        '0900000001'
    ),
    (
        'nhanvien',
        '42fae8a13d42327abbb8d700b0e2a7452f4198a63dfd3c88d6d052ad6aee7f20',
        'NHAN_VIEN_BAI_XE',
        TRUE,
        'nhanvien@xeparking.vn',
        '0900000002'
    ),
    (
        'quanly',
        '2d16797d627b8acdb0ecdd3028102f52b87a73edaed769070fbdc6019f6c8710',
        'NGUOI_QUAN_LY',
        TRUE,
        'quanly@xeparking.vn',
        '0900000003'
    );


-- ============================================================
-- 6. LUOTGUIXE (lượt gửi mẫu - đã trả, để có dữ liệu thống kê)
--    Không tạo lượt "Đang gửi" để bãi khởi động ở trạng thái trống.
-- ============================================================
INSERT INTO luotguixe (
    bienso,
    maloaixe,
    mavitri,
    loaive,
    thoigianvao,
    thoigianra,
    tongphi,
    tinhtrang
) VALUES
    (
        '30A-12345', 2, 1, 'VE_LUOT',
        '2026-09-23 08:00:00', '2026-09-23 10:00:00', 40000, 'Đã trả'
    ),
    (
        '59B-67890', 1, 4, 'VE_LUOT',
        '2026-09-23 09:00:00', '2026-09-23 11:30:00', 15000, 'Đã trả'
    );
