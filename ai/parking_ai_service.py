import cv2

from ai.vehicle_detector import VehicleDetector
from ai.vehicle_classifier import VehicleClassifier
from ai.plate_detector import PlateDetector
from ai.plate_recognizer import PlateRecognizer


class ParkingAIService:

    def __init__(self):

        self.vehicle_detector = VehicleDetector()

        self.plate_detector = PlateDetector()

        self.plate_recognizer = PlateRecognizer()


    def process_image(self, image_path):

        # ====================================================
        # 1. ĐỌC ẢNH
        # ====================================================

        image = cv2.imread(image_path)

        if image is None:

            return {
                "success": False,
                "message": "Không thể đọc ảnh"
            }


        # ====================================================
        # 2. DETECT VEHICLE
        # ====================================================

        vehicles = self.vehicle_detector.detect(
            image_path
        )

        if not vehicles:

            return {
                "success": False,
                "message": "Không phát hiện phương tiện"
            }


        # Chọn phương tiện có confidence cao nhất

        vehicle = max(
            vehicles,
            key=lambda x: x["confidence"]
        )


        # ====================================================
        # 3. CLASSIFY VEHICLE
        # ====================================================

        vehicle_type = VehicleClassifier.classify(
            vehicle["class_name"]
        )


        # ====================================================
        # 4. DETECT LICENSE PLATE
        # ====================================================

        plates = self.plate_detector.detect(
            image_path
        )

        if not plates:

            return {
                "success": False,
                "message": "Không phát hiện biển số xe",
                "vehicle": {
                    "class_name": vehicle["class_name"],
                    "confidence": vehicle["confidence"],
                    "bbox": vehicle["bbox"]
                }
            }


        # Chọn biển số có confidence cao nhất

        plate = max(
            plates,
            key=lambda x: x["confidence"]
        )


        # ====================================================
        # 5. CROP LICENSE PLATE
        # ====================================================

        x1, y1, x2, y2 = plate["bbox"]


        image_height, image_width = image.shape[:2]


        box_width = x2 - x1

        box_height = y2 - y1


        # Padding giống phần test OCR đã ổn định

        padding_left = int(
            box_width * 0.05
        )

        padding_right = int(
            box_width * 0.25
        )

        padding_top = int(
            box_height * 0.15
        )

        padding_bottom = int(
            box_height * 0.15
        )


        crop_x1 = max(
            0,
            x1 - padding_left
        )

        crop_y1 = max(
            0,
            y1 - padding_top
        )

        crop_x2 = min(
            image_width,
            x2 + padding_right
        )

        crop_y2 = min(
            image_height,
            y2 + padding_bottom
        )


        plate_image = image[
            crop_y1:crop_y2,
            crop_x1:crop_x2
        ]


        if plate_image.size == 0:

            return {
                "success": False,
                "message": "Không thể crop biển số"
            }


        # ====================================================
        # 6. OCR
        # ====================================================

        ocr_result = self.plate_recognizer.recognize(
            plate_image
        )


        if not ocr_result:

            return {
                "success": False,
                "message": "Không nhận diện được ký tự biển số",
                "vehicle": {
                    "class_name": vehicle["class_name"],
                    "vehicle_type": vehicle_type,
                    "confidence": vehicle["confidence"]
                },
                "plate_detection": {
                    "confidence": plate["confidence"],
                    "bbox": plate["bbox"]
                }
            }


        # ====================================================
        # 7. KẾT QUẢ
        # ====================================================

        return {

            "success": True,

            "message": "AI nhận diện phương tiện thành công",

            "data": {

                "bienso": ocr_result["text"],

                "ocr_confidence": ocr_result["confidence"],

                "loaixe": vehicle_type,

                "vehicle_class": vehicle["class_name"],

                "vehicle_confidence": vehicle["confidence"],

                "plate_detection_confidence":
                    plate["confidence"],

                "vehicle_bbox":
                    vehicle["bbox"],

                "plate_bbox":
                    plate["bbox"]
            }
        }