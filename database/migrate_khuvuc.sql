-- ============================================================
-- XeParking - Migration: vitrido.tenkhuvuc → vitrido.makhuvuc
-- Supabase / PostgreSQL
-- ============================================================
--
-- DÙNG KHI NÀO
--
-- Chỉ dùng cho database ĐÃ CÓ dữ liệu và còn ở dạng cũ
-- (vitrido.tenkhuvuc kiểu chuỗi).
--
-- database/schema.sql dùng "CREATE TABLE IF NOT EXISTS", nên chạy nó
-- trên database đã tồn tại sẽ KHÔNG thay đổi gì cả — bảng vitrido vẫn
-- giữ cột tenkhuvuc, và seed.sql sau đó sẽ báo lỗi ở dòng
-- "INSERT INTO vitrido (makhuvuc, ...)".
--
-- Database tạo mới hoàn toàn thì KHÔNG cần file này: chạy thẳng
-- schema.sql rồi seed.sql là xong.
--
-- CÁCH CHẠY
--
-- Mở Supabase → SQL Editor → dán toàn bộ file này → Run.
--
-- Script chạy trong một transaction. Nếu dữ liệu không khớp khu vực,
-- bước 3 sẽ tự RAISE EXCEPTION và hủy toàn bộ — database giữ nguyên
-- trạng thái cũ, không bị sửa dở dang.
--
-- Sau khi chạy xong, chạy lại database/seed.sql để nạp dữ liệu mẫu.
-- ============================================================

BEGIN;

-- ============================================================
-- 0. SAO LƯU
--
-- Giữ nguyên bản vitrido trước khi sửa. Xóa bảng này bằng tay sau
-- khi đã kiểm tra hệ thống chạy đúng.
-- ============================================================

CREATE TABLE IF NOT EXISTS vitrido_backup AS
SELECT * FROM vitrido;

-- ============================================================
-- 1. THÊM CỘT MỚI (tạm cho phép NULL)
-- ============================================================

ALTER TABLE vitrido
    ADD COLUMN IF NOT EXISTS makhuvuc INTEGER;

-- ============================================================
-- 2. ĐỔ DỮ LIỆU TỪ TÊN KHU VỰC SANG MÃ KHU VỰC
-- ============================================================

UPDATE vitrido v
SET makhuvuc = k.makhuvuc
FROM khuvuc k
WHERE k.tenkhuvuc = v.tenkhuvuc;

-- ============================================================
-- 3. CHỐT AN TOÀN
--
-- Nếu còn dòng nào không tra được khu vực (tên khu vực trong vitrido
-- không khớp bảng khuvuc), dừng ngay và hủy transaction. Chạy truy
-- vấn dưới đây để xem thủ công trước khi sửa dữ liệu:
--
--     SELECT v.mavitri, v.tenkhuvuc
--     FROM vitrido v
--     LEFT JOIN khuvuc k ON k.tenkhuvuc = v.tenkhuvuc
--     WHERE k.makhuvuc IS NULL;
-- ============================================================

DO $$
DECLARE
    so_dong_loi INTEGER;
BEGIN
    SELECT count(*) INTO so_dong_loi
    FROM vitrido
    WHERE makhuvuc IS NULL;

    IF so_dong_loi > 0 THEN
        RAISE EXCEPTION
            'Có % vị trí đỗ không khớp được khu vực nào. Migration đã hủy, database chưa thay đổi.',
            so_dong_loi;
    END IF;
END $$;

-- ============================================================
-- 4. BẮT BUỘC NOT NULL
-- ============================================================

ALTER TABLE vitrido
    ALTER COLUMN makhuvuc SET NOT NULL;

-- ============================================================
-- 5. BỎ KHÓA NGOẠI CŨ VÀ CỘT CŨ
--
-- Bắt buộc phải bỏ constraint cũ trước khi bỏ cột: database cũ đã có
-- constraint tên "fk_vitrido_khuvuc" trỏ vào tenkhuvuc, nên bước 6 sẽ
-- báo trùng tên nếu chưa dọn.
-- ============================================================

ALTER TABLE vitrido
    DROP CONSTRAINT IF EXISTS fk_vitrido_khuvuc;

ALTER TABLE vitrido
    DROP COLUMN IF EXISTS tenkhuvuc;

-- ============================================================
-- 6. GẮN KHÓA NGOẠI MỚI
-- ============================================================

ALTER TABLE vitrido
    ADD CONSTRAINT fk_vitrido_khuvuc
    FOREIGN KEY (makhuvuc) REFERENCES khuvuc(makhuvuc);

-- ============================================================
-- 7. ĐỒNG BỘ RÀNG BUỘC CHECK VỚI schema.sql
--
-- Database cũ có thể chưa có ràng buộc này. PostgreSQL không hỗ trợ
-- "ADD CONSTRAINT IF NOT EXISTS" nên phải kiểm tra qua pg_constraint.
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_vitrido_trangthai'
          AND conrelid = 'vitrido'::regclass
    ) THEN
        ALTER TABLE vitrido
            ADD CONSTRAINT chk_vitrido_trangthai
            CHECK (trangthai IN ('Còn trống', 'Đang sử dụng'));
    END IF;
END $$;

COMMIT;

-- ============================================================
-- KIỂM TRA SAU KHI CHẠY
-- ============================================================
--
--     -- Phải trả về 6 (hoặc đúng số vị trí đang có), không có NULL
--     SELECT mavitri, makhuvuc, trangthai FROM vitrido ORDER BY mavitri;
--
--     -- Bản sao lưu vẫn còn nguyên
--     SELECT count(*) FROM vitrido_backup;
--
--     -- Dọn bản sao lưu khi đã chắc chắn
--     -- DROP TABLE vitrido_backup;
-- ============================================================
