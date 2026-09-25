"""
Huấn luyện model nhận diện biển số (YOLO11).

Cách dùng:

    python train_plate.py --data archive/dataset.yaml

Sau khi xong, trọng số tốt nhất được chép vào models/license_plate.pt.

LƯU Ý VỀ DATASET
----------------
Thư mục archive/ kèm theo dự án hiện KHÔNG huấn luyện lại được: chỉ có
ảnh .png, thiếu toàn bộ file nhãn .txt và thiếu images/val/ mà
dataset.yaml trỏ tới. Muốn huấn luyện lại, cần bộ dữ liệu có nhãn đầy
đủ. File models/license_plate.pt đã huấn luyện mới là thứ dùng để chạy.
"""

import argparse
import os
import shutil

from ultralytics import YOLO


MAC_DINH_DATASET = "archive/dataset.yaml"
MAC_DINH_MODEL_NEN = "yolo11n.pt"
MAC_DINH_KET_QUA = "models/license_plate.pt"


def train_plate_model(
    yaml_path,
    model_nen=MAC_DINH_MODEL_NEN,
    so_epoch=10,
    kich_thuoc_anh=640,
    batch=16,
    thiet_bi="cpu",
    ten_lan_chay="plate_detector_run",
    ket_qua=MAC_DINH_KET_QUA
):
    if not os.path.exists(yaml_path):
        raise SystemExit(
            f"Không thấy file cấu hình dataset: {yaml_path}\n"
            "Truyền đường dẫn đúng bằng --data, ví dụ:\n"
            "    python train_plate.py --data archive/dataset.yaml"
        )

    print(f"Bắt đầu huấn luyện YOLO cho nhận diện biển số")
    print(f"    dataset : {yaml_path}")
    print(f"    model nền: {model_nen}")
    print(f"    epoch   : {so_epoch} | imgsz {kich_thuoc_anh} | batch {batch} | device {thiet_bi}")

    model = YOLO(model_nen)

    results = model.train(
        data=yaml_path,
        epochs=so_epoch,
        imgsz=kich_thuoc_anh,
        batch=batch,
        device=thiet_bi,
        name=ten_lan_chay
    )

    print("Huấn luyện xong.")

    best_weight_path = os.path.join(
        results.save_dir,
        "weights",
        "best.pt"
    )

    if not os.path.exists(best_weight_path):
        raise SystemExit(
            f"Không thấy best.pt tại: {best_weight_path}\n"
            "Kiểm tra thư mục runs/ để lấy trọng số thủ công."
        )

    os.makedirs(os.path.dirname(ket_qua) or ".", exist_ok=True)
    shutil.copy(best_weight_path, ket_qua)

    print(f"Đã chép trọng số tốt nhất vào {ket_qua}")


def main():
    parser = argparse.ArgumentParser(
        description="Huấn luyện model nhận diện biển số cho XeParking."
    )

    parser.add_argument(
        "--data",
        default=MAC_DINH_DATASET,
        help=f"Đường dẫn dataset.yaml (mặc định: {MAC_DINH_DATASET})"
    )
    parser.add_argument(
        "--model-nen",
        default=MAC_DINH_MODEL_NEN,
        help=f"Trọng số nền để fine-tune (mặc định: {MAC_DINH_MODEL_NEN})"
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument(
        "--device",
        default="cpu",
        help='Thiết bị huấn luyện: "cpu", "0" cho GPU đầu tiên (mặc định: cpu)'
    )
    parser.add_argument(
        "--name",
        default="plate_detector_run",
        help="Tên lần chạy, dùng đặt tên thư mục trong runs/"
    )
    parser.add_argument(
        "--output",
        default=MAC_DINH_KET_QUA,
        help=f"Nơi lưu trọng số tốt nhất (mặc định: {MAC_DINH_KET_QUA})"
    )

    args = parser.parse_args()

    train_plate_model(
        yaml_path=args.data,
        model_nen=args.model_nen,
        so_epoch=args.epochs,
        kich_thuoc_anh=args.imgsz,
        batch=args.batch,
        thiet_bi=args.device,
        ten_lan_chay=args.name,
        ket_qua=args.output
    )


if __name__ == "__main__":
    main()
