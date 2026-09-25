
import os

from ultralytics import YOLO

from ai.duong_dan import duong_dan


class PlateDetector:
    """
    Phát hiện biển số xe bằng model YOLO tự huấn luyện.

    Model hiện tại (models/license_plate.pt) có 2 lớp:

        0 → BSD   biển số dài (1 dòng)
        1 → BSV   biển số vuông (2 dòng)

    Cả hai đều là biển số hợp lệ. Bản trước lọc cứng "class_id != 0"
    nên bỏ sót toàn bộ biển vuông, khiến 2 endpoint
    /api/parking/ai-entry và /api/parking/ai-exit thất bại với loại
    biển này.

    Tên lớp được lấy trực tiếp từ model thay vì hardcode, để model
    huấn luyện lại với bộ lớp khác vẫn dùng được.
    """

    # Tên lớp được coi là biển số.
    TEN_LOP_BIEN_SO = {"BSD", "BSV"}

    def __init__(
        self,
        model_path=None
    ):
        if model_path is None:
            model_path = "models/license_plate.pt"

        # Neo vào gốc dự án, không tính theo thư mục đang đứng.
        model_path = duong_dan(model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Không tìm thấy model biển số: {model_path}"
            )

        self.model = YOLO(model_path)

        self.ten_lop = self._doc_ten_lop(self.model)

        # Nếu model không có lớp nào khớp tên đã biết (ví dụ model cũ
        # chỉ huấn luyện 1 lớp với tên khác), chấp nhận mọi lớp — thà
        # nhận thừa rồi để OCR lọc, còn hơn bỏ sót biển số.
        lop_bien_so = {
            ma_lop
            for ma_lop, ten in self.ten_lop.items()
            if str(ten).upper() in self.TEN_LOP_BIEN_SO
        }

        self.lop_chap_nhan = lop_bien_so or set(self.ten_lop)

    @staticmethod
    def _doc_ten_lop(model):
        """
        Chuẩn hóa model.names về dict {mã lớp: tên lớp}.

        Ultralytics trả về dict, nhưng một số bản trả về list.
        """
        ten_lop = getattr(model, "names", None)

        if isinstance(ten_lop, (list, tuple)):
            return {
                ma_lop: ten
                for ma_lop, ten in enumerate(ten_lop)
            }

        return dict(ten_lop or {})

    def _ten_lop_cua(self, ma_lop):
        return self.ten_lop.get(
            ma_lop,
            f"class_{ma_lop}"
        )

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

                if class_id not in self.lop_chap_nhan:
                    continue

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                plates.append({
                    "class_id": class_id,
                    "class_name": self._ten_lop_cua(class_id),
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
