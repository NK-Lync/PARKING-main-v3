# GenAI Analytics Skill

## File

ai/iai_provider.py

ai/he_thong_ai.py

routes/he_thong_ai.py

## Purpose

Dùng AI sinh (GenAI) để phân tích dữ liệu và hỗ trợ ra quyết định (UC14–UC17).

## Interface

```text
IAIProvider
    ├── sinh_bao_cao_luu_luong(data)
    ├── phan_tich_gio_cao_diem(data)
    ├── goi_y_bo_tri_nhan_su(data)
    └── hoi_dap_du_lieu(question, context)
```

## Config

```text
AI_API_URL      endpoint chat/completions
AI_API_KEY      khóa API
AI_MODEL_NAME   tên mô hình (mặc định gpt-4o)
```

## Logic

```text
Dữ liệu nghiệp vụ (ThongKeService)
        ↓
IAIProvider
        ↓
GenAI (nếu có API key)
        ↓
Báo cáo / gợi ý / câu trả lời
```

## Fallback

Khi không có API key, hệ thống chuyển sang chế độ phân tích nội bộ (deterministic) để vẫn hoạt động bình thường.

## Rules

GenAI chỉ phân tích dữ liệu được cung cấp, không tự tạo số liệu.

GenAI không được ghi dữ liệu nghiệp vụ trực tiếp.

## API

```text
POST /api/ai/bao-cao-luu-luong
POST /api/ai/gio-cao-diem
POST /api/ai/goi-y-nhan-su
POST /api/ai/hoi-dap
```

## Core Rule

```text
Data is truth.
GenAI is analyst.
Business decides.
```
