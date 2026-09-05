
from ultralytics import YOLO


class PlateDetector:

    def __init__(
        self,
        model_path="models/license_plate.pt"
    ):
        self.model = YOLO(model_path)

    def detect(self, image):

        results = self.model.predict(
            source=image,
            conf=0.15,
            imgsz=1280,
            iou=0.45,
            max_det=10,
            verbose=False
        )

        plates = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])

                if class_id != 0:
                    continue

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                plates.append({
                    "class_id": class_id,
                    "class_name": "license_plate",
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

        # Sắp xếp theo confidence
        plates.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        # Chỉ giữ detection tốt nhất
        if plates:
            return [plates[0]]

        return []

