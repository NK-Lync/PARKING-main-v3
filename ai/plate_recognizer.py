import re
import cv2
import easyocr


class PlateRecognizer:

    def __init__(self):
        self.reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

    def preprocess(self, plate_image):
        gray = cv2.cvtColor(
            plate_image,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0
        )

        return gray

    def normalize_plate(self, text):
        text = text.upper()

        # Loại bỏ ký tự không hợp lệ
        text = re.sub(
            r"[^A-Z0-9]",
            "",
            text
        )

        return text

    def correct_common_ocr_errors(self, text):
        """
        Sửa một số lỗi OCR phổ biến trên biển số Việt Nam.
        """

        text = text.upper()

        # OCR thường nhầm O thành 0 hoặc ngược lại.
        # Với vị trí đầu biển số, ký tự đầu tiên thường là số.
        if len(text) >= 2:
            if text[0] == "O":
                text = "0" + text[1:]

        # Hai ký tự đầu của biển số thường là mã tỉnh/thành.
        # Nếu OCR nhận O ở vị trí thứ 2 thì sửa thành 0.
        if len(text) >= 2:
            if text[1] == "O":
                text = text[0] + "0" + text[2:]

        # Trong phần số cuối, O thường được OCR nhầm thành 0.
        # Ngược lại, không tự động đổi mọi 0 thành O vì 0 xuất hiện rất phổ biến.
        text = text.replace("O", "0")

        return text

    def validate_plate(self, text):
        """
        Kiểm tra biển số có hình thức tương đối hợp lệ hay không.

        Ví dụ:
        30A69696
        29B12345
        51F12345
        """

        if not text:
            return False

        # Biển số dân dụng dạng:
        # 2 số + 1 chữ + 4-6 số
        pattern = r"^[0-9]{2}[A-Z][0-9]{4,6}$"

        return bool(
            re.fullmatch(pattern, text)
        )

    def recognize(self, plate_image):

        if plate_image is None:
            return None

        if plate_image.size == 0:
            return None

        processed = self.preprocess(
            plate_image
        )

        results = self.reader.readtext(
            processed,
            detail=1,
            paragraph=False
        )

        if not results:
            return None

        candidates = []

        for result in results:

            text = result[1]
            confidence = float(result[2])

            normalized = self.normalize_plate(
                text
            )

            if not normalized:
                continue

            corrected = self.correct_common_ocr_errors(
                normalized
            )

            candidates.append({
                "text": corrected,
                "raw_text": normalized,
                "confidence": confidence,
                "valid": self.validate_plate(
                    corrected
                )
            })

        if not candidates:
            return None

        # Ưu tiên candidate có format biển số hợp lệ.
        valid_candidates = [
            candidate
            for candidate in candidates
            if candidate["valid"]
        ]

        if valid_candidates:
            valid_candidates.sort(
                key=lambda x: x["confidence"],
                reverse=True
            )

            return valid_candidates[0]

        # Nếu không có candidate hợp lệ,
        # vẫn trả về candidate có confidence cao nhất.
        candidates.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        return candidates[0]