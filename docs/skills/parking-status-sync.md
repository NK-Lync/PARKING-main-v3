# Parking Status Sync Skill

## File

services/parking_service.py

## Method

sync_ai_occupancy()

## Purpose

Đồng bộ trạng thái AI → Supabase.

## Business Protection

Nếu LuotGuiXe active tồn tại:

AI không được phép chuyển

Đang sử dụng
→
Còn trống

## Priority

LuotGuiXe
>
AI Detection