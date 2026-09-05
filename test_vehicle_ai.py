from ai.vehicle_detector import VehicleDetector


detector = VehicleDetector()

image_path = "test.jpg"

vehicles = detector.detect(image_path)

print("Kết quả nhận diện:")

for vehicle in vehicles:

    print(
        f"- {vehicle['class_name']} "
        f"| confidence={vehicle['confidence']:.2f} "
        f"| bbox={vehicle['bbox']}"
    )