import os

from ultralytics import YOLO

from ai.duong_dan import duong_dan


class VehicleDetector:

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = "yolo11n.pt"

        # Neo vào gốc dự án, không tính theo thư mục đang đứng.
        model_path = duong_dan(model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Không tìm thấy model phát hiện xe: {model_path}"
            )

        self.model = YOLO(model_path)

    def detect(self, image):
        results = self.model(image)

        vehicles = []

        vehicle_classes = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])

                if class_id not in vehicle_classes:
                    continue

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                vehicles.append({
                    "class_id": class_id,
                    "class_name": vehicle_classes[class_id],
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

        return vehicles