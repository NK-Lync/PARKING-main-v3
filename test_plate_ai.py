from ai.plate_detector import PlateDetector


detector = PlateDetector()

image_path = "test.jpg"

plates = detector.detect(image_path)

print("Kết quả phát hiện biển số:")

if not plates:
    print("Không tìm thấy biển số.")

else:

    for index, plate in enumerate(plates, start=1):

        print(
            f"Biển số {index}: "
            f"confidence={plate['confidence']:.2f} "
            f"bbox={plate['bbox']}"
        )