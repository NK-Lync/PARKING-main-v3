# API Skill

## Purpose

Quản lý toàn bộ REST API của XeParking.

## Routes

### Parking

POST /api/parking/entry

POST /api/parking/exit

GET /api/parking/status

POST /api/parking/ai-entry

POST /api/parking/ai-exit

POST /api/parking/ai-status

## Rules

- Response phải có success
- Response phải có message
- Dữ liệu nghiệp vụ nằm trong data
- HTTP 200 cho nghiệp vụ thành công
- HTTP 400 cho lỗi nghiệp vụ
- HTTP 500 cho lỗi hệ thống