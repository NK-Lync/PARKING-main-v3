# Parking Occupancy Skill

## File

ai/parking_occupancy.py

## Config

config/parking_slots.json

## Purpose

Xác định ô đỗ nào đang có xe.

## Logic

Vehicle Detection
↓
Bottom Center Point
↓
Point In Polygon
↓
Assign Slot

## Slot Status

Còn trống

Đang sử dụng

## Output

{
    "tong_vi_tri":6,
    "dang_su_dung":1,
    "con_trong":5,
    "vi_tri":[]
}