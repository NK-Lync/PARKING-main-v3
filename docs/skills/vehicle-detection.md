# Vehicle Detection Skill

## File

ai/vehicle_detector.py

## Model

YOLO

## Purpose

Nhận diện phương tiện trong ảnh.

## Output

[
    {
        "class_name":"car",
        "confidence":0.89,
        "bbox":[x1,y1,x2,y2]
    }
]

## Supported Classes

- car
- motorcycle
- bus
- truck

## Used By

parking_occupancy.py

ai-entry

ai-status