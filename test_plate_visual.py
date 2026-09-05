from ultralytics import YOLO


model = YOLO("models/license_plate.pt")

results = model.predict(
    source="test.jpg",
    conf=0.10,
    save=True,
    verbose=True
)

print("Đã xử lý xong.")
print("Ảnh kết quả được lưu trong thư mục runs/detect/")