-- ============================================================
-- Migration: Thêm bảng kiểm soát AI qua DB và lưu lịch sử prompt
-- Chạy script này trong Supabase SQL Editor
-- ============================================================

-- 1. Bảng lưu lịch sử prompt và phản hồi từ AI
CREATE TABLE IF NOT EXISTS ai_prompt_logs (
    id                SERIAL PRIMARY KEY,
    prompt_type       VARCHAR(50)  NOT NULL, -- 'bao_cao', 'gio_cao_diem', 'goi_y_nhan_su', 'hoi_dap'
    system_prompt     TEXT         NOT NULL,
    user_prompt       TEXT         NOT NULL,
    response_content  TEXT,                  -- Nội dung phản hồi từ AI hoặc nội bộ
    model_name        VARCHAR(100) NOT NULL,
    status            VARCHAR(20)  NOT NULL, -- 'SUCCESS', 'FALLBACK', 'ERROR'
    error_message     TEXT,                  -- Chi tiết lỗi nếu có
    created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ai_prompt_logs IS 'Lịch sử prompt gửi tới AI và phản hồi';

-- 2. Bảng cấu hình AI điều khiển qua database
CREATE TABLE IF NOT EXISTS ai_system_config (
    config_key        VARCHAR(100) PRIMARY KEY,
    config_value      TEXT         NOT NULL,
    description       TEXT,
    updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ai_system_config IS 'Cấu hình hệ thống AI điều khiển trực tiếp qua cơ sở dữ liệu';

-- Chèn dữ liệu cấu hình mặc định
INSERT INTO ai_system_config (config_key, config_value, description)
VALUES 
    ('AI_ENABLED', 'true', 'Bật/tắt dịch vụ AI chung'),
    ('AI_DEFAULT_TEMPERATURE', '0.3', 'Độ sáng tạo (temperature) của AI'),
    ('AI_MAX_TOKENS', '1000', 'Số lượng token tối đa trong phản hồi')
ON CONFLICT (config_key) DO NOTHING;
