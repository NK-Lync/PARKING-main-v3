
import cv2
import os

from ai.plate_detector import PlateDetector
from ai.plate_recognizer import PlateRecognizer


# ============================================================
# CẤU HÌNH
# ============================================================

IMAGE_PATH = "test.jpg"

OUTPUT_DIR = "runs/plate_ocr"


# Bbox của model hiện đang hơi thiếu về phía bên phải.
# Vì vậy:
# - Trái: chỉ mở rộng 5%
# - Phải: mở rộng 25%
# - Trên: mở rộng 15%
# - Dưới: mở rộng 15%

PADDING_LEFT = 0.05
PADDING_RIGHT = 0.25
PADDING_TOP = 0.15
PADDING_BOTTOM = 0.15


# ============================================================
# TẠO THƯ MỤC OUTPUT
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# ĐỌC ẢNH
# ============================================================

image = cv2.imread(
    IMAGE_PATH
)


if image is None:

    print(
        "Không thể đọc ảnh:",
        IMAGE_PATH
    )

    exit()


image_height, image_width = image.shape[:2]


print()
print(
    "========================================"
)

print(
    "THÔNG TIN ẢNH"
)

print(
    "========================================"
)

print(
    "Image size:",
    image_width,
    "x",
    image_height
)


# ============================================================
# KHỞI TẠO AI
# ============================================================

detector = PlateDetector()

recognizer = PlateRecognizer()


# ============================================================
# DETECT BIỂN SỐ
# ============================================================

plates = detector.detect(
    IMAGE_PATH
)


print()
print(
    "Số biển số phát hiện:",
    len(plates)
)


if not plates:

    print()
    print(
        "Không tìm thấy biển số."
    )

    exit()


# ============================================================
# XỬ LÝ TỪNG BIỂN SỐ
# ============================================================

for index, plate in enumerate(
    plates,
    start=1
):

    # --------------------------------------------------------
    # BBOX GỐC TỪ YOLO
    # --------------------------------------------------------

    x1, y1, x2, y2 = plate["bbox"]


    # --------------------------------------------------------
    # KÍCH THƯỚC BBOX
    # --------------------------------------------------------

    box_width = x2 - x1

    box_height = y2 - y1


    # --------------------------------------------------------
    # TÍNH PADDING RIÊNG CHO TỪNG PHÍA
    # --------------------------------------------------------

    padding_left = int(
        box_width * PADDING_LEFT
    )

    padding_right = int(
        box_width * PADDING_RIGHT
    )

    padding_top = int(
        box_height * PADDING_TOP
    )

    padding_bottom = int(
        box_height * PADDING_BOTTOM
    )


    # --------------------------------------------------------
    # MỞ RỘNG BBOX
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # CROP BIỂN SỐ
    # --------------------------------------------------------

    plate_image = image[
        crop_y1:crop_y2,
        crop_x1:crop_x2
    ]


    if plate_image.size == 0:

        print()
        print(
            f"Biển số {index}: Crop không hợp lệ."
        )

        continue


    # --------------------------------------------------------
    # LƯU CROP
    # --------------------------------------------------------

    crop_path = os.path.join(
        OUTPUT_DIR,
        f"plate_{index}.jpg"
    )


    cv2.imwrite(
        crop_path,
        plate_image
    )


    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    result = recognizer.recognize(
        plate_image
    )


    # ========================================================
    # IN KẾT QUẢ
    # ========================================================

    print()

    print(
        "========================================"
    )

    print(
        f"===== Biển số {index} ====="
    )

    print(
        "========================================"
    )


    print(
        "BBox gốc:",
        plate["bbox"]
    )


    print(
        "Kích thước BBox:",
        f"{box_width} x {box_height}"
    )


    print(
        "Padding trái:",
        padding_left,
        "px"
    )


    print(
        "Padding phải:",
        padding_right,
        "px"
    )


    print(
        "Padding trên:",
        padding_top,
        "px"
    )


    print(
        "Padding dưới:",
        padding_bottom,
        "px"
    )


    print(
        "BBox sau padding:",
        [
            crop_x1,
            crop_y1,
            crop_x2,
            crop_y2
        ]
    )


    print(
        "Detection confidence:",
        round(
            plate["confidence"],
            3
        )
    )


    print(
        "Crop:",
        crop_path
    )


    # --------------------------------------------------------
    # OCR RESULT
    # --------------------------------------------------------

    if result:

        print(
            "OCR:",
            result["text"]
        )

        print(
            "OCR confidence:",
            round(
                result["confidence"],
                3
            )
        )

    else:

        print(
            "OCR: Không nhận diện được"
        )


print()

print(
    "========================================"
)

print(
    "HOÀN TẤT"
)

print(
    "========================================"
)

print(
    f"Ảnh crop được lưu tại: {OUTPUT_DIR}"
)
