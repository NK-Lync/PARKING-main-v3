import json
import os

import cv2
import numpy as np

from ai.vehicle_detector import VehicleDetector


class ParkingOccupancyDetector:

    def __init__(
        self,
        config_path="config/parking_slots.json"
    ):
        self.vehicle_detector = VehicleDetector()

        # Thư mục gốc của project
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.config_path = os.path.join(
            project_root,
            config_path
        )

        self.parking_slots = (
            self.load_parking_slots()
        )

    def load_parking_slots(self):

        if not os.path.exists(
            self.config_path
        ):
            raise FileNotFoundError(
                f"Không tìm thấy file cấu hình: "
                f"{self.config_path}"
            )

        with open(
            self.config_path,
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(file)

        parking_slots = {}

        for key, value in config.items():

            mavitri = int(key)

            polygon = value["polygon"]

            if len(polygon) < 3:
                raise ValueError(
                    f"Polygon của vị trí "
                    f"{mavitri} phải có ít nhất "
                    f"3 điểm"
                )

            parking_slots[mavitri] = {
                "name": value.get(
                    "name",
                    f"Vị trí {mavitri}"
                ),
                "polygon": polygon
            }

        return parking_slots

    @staticmethod
    def normalized_to_pixel(
        polygon,
        image_width,
        image_height
    ):
        """
        Chuyển tọa độ chuẩn hóa
        [0.0 -> 1.0]
        thành tọa độ pixel.
        """

        pixel_polygon = []

        for point in polygon:

            normalized_x = float(
                point[0]
            )

            normalized_y = float(
                point[1]
            )

            pixel_x = int(
                normalized_x
                * image_width
            )

            pixel_y = int(
                normalized_y
                * image_height
            )

            pixel_polygon.append(
                [pixel_x, pixel_y]
            )

        return pixel_polygon

    @staticmethod
    def get_bottom_center(bbox):

        x1, y1, x2, y2 = bbox

        center_x = (
            x1 + x2
        ) / 2

        bottom_y = y2

        return center_x, bottom_y

    @staticmethod
    def point_inside_slot(
        point_x,
        point_y,
        polygon
    ):

        contour = np.array(
            polygon,
            dtype=np.int32
        )

        result = cv2.pointPolygonTest(
            contour,
            (
                float(point_x),
                float(point_y)
            ),
            False
        )

        return result >= 0

    def detect(self, image_path):

        image = cv2.imread(
            image_path
        )

        if image is None:
            return {
                "success": False,
                "message":
                    "Không thể đọc ảnh"
            }

        image_height, image_width = (
            image.shape[:2]
        )

        # YOLO phát hiện phương tiện
        vehicles = (
            self.vehicle_detector.detect(
                image_path
            )
        )

        # Khởi tạo trạng thái
        slots = {}

        for (
            mavitri,
            slot_config
        ) in self.parking_slots.items():

            normalized_polygon = (
                slot_config["polygon"]
            )

            pixel_polygon = (
                self.normalized_to_pixel(
                    normalized_polygon,
                    image_width,
                    image_height
                )
            )

            slots[mavitri] = {

                "mavitri":
                    mavitri,

                "name":
                    slot_config["name"],

                "polygon":
                    pixel_polygon,

                "trangthai":
                    "Còn trống",

                "vehicle":
                    None
            }

        # Kiểm tra từng phương tiện
        for vehicle in vehicles:

            center_x, bottom_y = (
                self.get_bottom_center(
                    vehicle["bbox"]
                )
            )

            # Tìm vị trí chứa xe
            for (
                mavitri,
                slot
            ) in slots.items():

                polygon = slot["polygon"]

                is_inside = (
                    self.point_inside_slot(
                        center_x,
                        bottom_y,
                        polygon
                    )
                )

                if not is_inside:
                    continue

                current_vehicle = (
                    slot["vehicle"]
                )

                # Nếu vị trí chưa có xe
                # hoặc xe hiện tại có confidence thấp hơn
                if (
                    current_vehicle is None
                    or
                    vehicle["confidence"]
                    >
                    current_vehicle["confidence"]
                ):

                    slot["trangthai"] = (
                        "Đang sử dụng"
                    )

                    slot["vehicle"] = {

                        "class_name":
                            vehicle[
                                "class_name"
                            ],

                        "confidence":
                            vehicle[
                                "confidence"
                            ],

                        "bbox":
                            vehicle[
                                "bbox"
                            ]
                    }

                # Một xe chỉ thuộc một vị trí
                break

        slot_list = list(
            slots.values()
        )

        tong_vi_tri = len(
            slot_list
        )

        dang_su_dung = sum(
            1
            for slot in slot_list
            if slot["trangthai"]
            == "Đang sử dụng"
        )

        con_trong = (
            tong_vi_tri
            -
            dang_su_dung
        )

        if tong_vi_tri > 0:

            ty_le_lap_day = round(
                dang_su_dung
                /
                tong_vi_tri
                *
                100,
                2
            )

        else:

            ty_le_lap_day = 0

        return {

            "success":
                True,

            "message":
                "AI nhận diện trạng thái "
                "bãi xe thành công",

            "data": {

                "tong_vi_tri":
                    tong_vi_tri,

                "dang_su_dung":
                    dang_su_dung,

                "con_trong":
                    con_trong,

                "ty_le_lap_day":
                    ty_le_lap_day,

                "vi_tri":
                    slot_list
            }
        }