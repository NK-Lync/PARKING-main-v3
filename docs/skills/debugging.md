# Debugging Skill

## Common Checks

### OCR

print(ocr_result)

### Vehicle Detection

print(vehicle_result)

### Occupancy

print(slot_result)

### Parking Service

print(parking_response)

## AI Status Debug

AI
↓
Occupancy
↓
Sync
↓
Supabase

## Verify

GET /api/parking/status

POST /api/parking/ai-status