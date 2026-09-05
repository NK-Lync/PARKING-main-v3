# License Plate Detection Skill

## File

ai/license_plate_detector.py

## Purpose

Xác định vị trí biển số xe.

## Output

{
    "bbox":[x1,y1,x2,y2],
    "confidence":0.92
}

## Pipeline

Image
↓
Vehicle
↓
Plate Detection
↓
Crop Plate