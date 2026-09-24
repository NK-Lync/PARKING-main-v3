
from flask import Blueprint, request, Response
import json
import os
import tempfile

from services.parking_service import ParkingService
from services.loai_xe_service import LoaiXeService

from ai.parking_ai_service import ParkingAIService
from ai.parking_occupancy import ParkingOccupancyDetector


parking_bp = Blueprint(
    "parking",
    __name__,
    url_prefix="/api/parking"
)


# ============================================================
# JSON RESPONSE
# ============================================================

def json_response(data, status_code=200):

    body = json.dumps(
        data,
        ensure_ascii=False
    )

    return Response(
        body.encode("utf-8"),
        status=status_code,
        content_type="application/json; charset=utf-8"
    )


# ============================================================
# AI SERVICES
#
# Lazy-load: chỉ khởi tạo model khi endpoint AI vision thực sự
# được gọi. Nhờ vậy app khởi động được ngay cả khi chưa có file
# model (ví dụ models/license_plate.pt chưa được huấn luyện).
# ============================================================

_parking_ai_service = None
_parking_occupancy_detector = None


def _get_parking_ai_service():
    global _parking_ai_service
    if _parking_ai_service is None:
        _parking_ai_service = ParkingAIService()
    return _parking_ai_service


def _get_parking_occupancy_detector():
    global _parking_occupancy_detector
    if _parking_occupancy_detector is None:
        _parking_occupancy_detector = ParkingOccupancyDetector()
    return _parking_occupancy_detector


# ============================================================
# 1. XE VÀO BÃI - THỦ CÔNG
# ============================================================

@parking_bp.route(
    "/entry",
    methods=["POST"]
)
def vehicle_entry():

    data = request.get_json(
        silent=True
    )

    if not data:

        return json_response(
            {
                "success": False,
                "message":
                    "Dữ liệu JSON không hợp lệ"
            },
            400
        )

    bien_so = data.get(
        "bienso"
    )

    ma_loai_xe = data.get(
        "maloaixe"
    )

    if not bien_so:

        return json_response(
            {
                "success": False,
                "message":
                    "Thiếu biển số xe"
            },
            400
        )

    if ma_loai_xe is None:

        return json_response(
            {
                "success": False,
                "message":
                    "Thiếu mã loại xe"
            },
            400
        )

    result = ParkingService.vehicle_entry(
        bien_so,
        ma_loai_xe
    )

    if not result["success"]:

        return json_response(
            result,
            400
        )

    return json_response(
        result,
        201
    )


# ============================================================
# 2. XE RA KHỎI BÃI - THỦ CÔNG
# ============================================================

@parking_bp.route(
    "/exit",
    methods=["POST"]
)
def vehicle_exit():

    data = request.get_json(
        silent=True
    )

    if not data:

        return json_response(
            {
                "success": False,
                "message":
                    "Dữ liệu JSON không hợp lệ"
            },
            400
        )

    bien_so = data.get(
        "bienso"
    )

    if not bien_so:

        return json_response(
            {
                "success": False,
                "message":
                    "Thiếu biển số xe"
            },
            400
        )

    result = ParkingService.vehicle_exit(
        bien_so
    )

    if not result["success"]:

        return json_response(
            result,
            400
        )

    return json_response(
        result,
        200
    )


# ============================================================
# 3. TRẠNG THÁI BÃI XE
# ============================================================

@parking_bp.route(
    "/status",
    methods=["GET"]
)
def parking_status():

    result = ParkingService.get_status()

    if not result["success"]:

        return json_response(
            result,
            400
        )

    return json_response(
        result,
        200
    )


# ============================================================
# 4. AI ENTRY
#
# Luồng:
#
# Camera
#   ↓
# Vehicle Detection
#   ↓
# Plate Detection
#   ↓
# OCR
#   ↓
# Vehicle Classification
#   ↓
# Parking Occupancy Detection
#   ↓
# Xác định vị trí
#   ↓
# vehicle_entry_at_position()
#   ↓
# Supabase
#
# ============================================================

@parking_bp.route(
    "/ai-entry",
    methods=["POST"]
)
def ai_vehicle_entry():

    if "image" not in request.files:

        return json_response(
            {
                "success": False,
                "message":
                    "Thiếu file ảnh"
            },
            400
        )

    image_file = request.files[
        "image"
    ]

    if image_file.filename == "":

        return json_response(
            {
                "success": False,
                "message":
                    "Tên file ảnh không hợp lệ"
            },
            400
        )

    temp_path = None

    try:

        # ====================================================
        # LƯU ẢNH TẠM
        # ====================================================

        suffix = os.path.splitext(
            image_file.filename
        )[1]

        if not suffix:
            suffix = ".jpg"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            image_file.save(
                temp_file.name
            )

            temp_path = temp_file.name

        # ====================================================
        # BƯỚC 1
        # AI NHẬN DIỆN XE + BIỂN SỐ
        # ====================================================

        ai_result = (
            _get_parking_ai_service()
            .process_image(
                temp_path
            )
        )

        if not ai_result["success"]:

            return json_response(
                {
                    "success": False,
                    "message":
                        ai_result.get(
                            "message",
                            "AI không thể nhận diện xe"
                        ),
                    "ai": ai_result
                },
                400
            )

        ai_data = ai_result.get(
            "data",
            {}
        )

        bien_so = ai_data.get(
            "bienso"
        )

        loaixe = ai_data.get(
            "loaixe"
        )

        # ----------------------------------------------------
        # Kiểm tra biển số
        # ----------------------------------------------------

        if not bien_so:

            return json_response(
                {
                    "success": False,
                    "message":
                        "AI không nhận diện được biển số",
                    "ai": ai_result
                },
                400
            )

        # ----------------------------------------------------
        # Kiểm tra loại xe
        # ----------------------------------------------------

        if not loaixe:

            return json_response(
                {
                    "success": False,
                    "message":
                        "AI không xác định được loại xe",
                    "ai": ai_result
                },
                400
            )

        # ====================================================
        # BƯỚC 2
        # TÌM MÃ LOẠI XE TRONG SUPABASE
        #
        # LoaiXeService.get_all()
        # trả về:
        #
        # [
        #   {
        #       "maloaixe": 1,
        #       "tenloaixe": "Xe máy",
        #       "dongia": 5000
        #   },
        #   {
        #       "maloaixe": 2,
        #       "tenloaixe": "Ô tô",
        #       "dongia": 20000
        #   }
        # ]
        #
        # ====================================================

        vehicle_types = (
            LoaiXeService.get_all()
        )

        if not vehicle_types:

            return json_response(
                {
                    "success": False,
                    "message":
                        "Không có loại xe trong hệ thống",
                    "ai": ai_result
                },
                400
            )

        # ----------------------------------------------------
        # Tìm loại xe AI nhận diện được
        # ----------------------------------------------------

        vehicle_type_data = None

        for vehicle_type in vehicle_types:

            database_vehicle_type = (
                vehicle_type.get(
                    "tenloaixe"
                )
            )

            if not database_vehicle_type:
                continue

            if (
                database_vehicle_type.strip().lower()
                ==
                loaixe.strip().lower()
            ):

                vehicle_type_data = (
                    vehicle_type
                )

                break

        # ----------------------------------------------------
        # Không tìm thấy loại xe
        # ----------------------------------------------------

        if vehicle_type_data is None:

            return json_response(
                {
                    "success": False,
                    "message":
                        (
                            "Loại xe AI nhận diện "
                            "không tồn tại trong hệ thống"
                        ),
                    "ai": ai_result,
                    "loaixe_ai": loaixe,
                    "cac_loai_xe":
                        vehicle_types
                },
                400
            )

        # ----------------------------------------------------
        # Lấy mã loại xe
        # ----------------------------------------------------

        ma_loai_xe = vehicle_type_data.get(
            "maloaixe"
        )

        if ma_loai_xe is None:

            return json_response(
                {
                    "success": False,
                    "message":
                        "Loại xe không có mã loại xe",
                    "ai": ai_result,
                    "loaixe": vehicle_type_data
                },
                400
            )

        # ====================================================
        # BƯỚC 3
        # AI XÁC ĐỊNH TRẠNG THÁI CÁC VỊ TRÍ
        # ====================================================

        occupancy_result = (
            _get_parking_occupancy_detector()
            .detect(
                temp_path
            )
        )

        if not occupancy_result["success"]:

            return json_response(
                {
                    "success": False,
                    "message":
                        (
                            "AI không xác định được "
                            "trạng thái vị trí"
                        ),
                    "ai": ai_result,
                    "occupancy":
                        occupancy_result
                },
                400
            )

        occupancy_data = (
            occupancy_result.get(
                "data",
                {}
            )
        )

        slot_list = (
            occupancy_data.get(
                "vi_tri",
                []
            )
        )

        if not slot_list:

            return json_response(
                {
                    "success": False,
                    "message":
                        (
                            "AI không trả về "
                            "danh sách vị trí"
                        ),
                    "ai": ai_result,
                    "occupancy":
                        occupancy_result
                },
                400
            )

        # ====================================================
        # BƯỚC 4
        # TÌM VỊ TRÍ AI XÁC ĐỊNH XE ĐANG ĐỨNG
        # ====================================================

        occupied_slots = []

        for slot in slot_list:

            if (
                slot.get("trangthai")
                == "Đang sử dụng"
                and
                slot.get("vehicle") is not None
            ):

                occupied_slots.append(
                    slot
                )

        if not occupied_slots:

            return json_response(
                {
                    "success": False,
                    "message":
                        (
                            "AI không xác định được "
                            "vị trí xe"
                        ),
                    "ai": ai_result,
                    "occupancy":
                        occupancy_result
                },
                400
            )

        # ====================================================
        # BƯỚC 5
        # MATCH VEHICLE BBOX
        #
        # ParkingAIService:
        #
        #     vehicle_bbox
        #
        # ParkingOccupancyDetector:
        #
        #     slot["vehicle"]["bbox"]
        #
        # Nếu trùng bbox -> xác định đúng slot.
        # ====================================================

        vehicle_bbox = (
            ai_data.get(
                "vehicle_bbox"
            )
        )

        selected_slot = None

        if vehicle_bbox:

            for slot in occupied_slots:

                slot_vehicle = (
                    slot.get(
                        "vehicle"
                    )
                )

                if not slot_vehicle:
                    continue

                slot_bbox = (
                    slot_vehicle.get(
                        "bbox"
                    )
                )

                if slot_bbox == vehicle_bbox:

                    selected_slot = slot

                    break

        # ====================================================
        # FALLBACK
        #
        # Nếu bbox không trùng tuyệt đối,
        # chọn vehicle có confidence cao nhất.
        # ====================================================

        if selected_slot is None:

            selected_slot = max(
                occupied_slots,
                key=lambda slot:
                    slot.get(
                        "vehicle",
                        {}
                    ).get(
                        "confidence",
                        0
                    )
            )

        # ====================================================
        # BƯỚC 6
        # LẤY MÃ VỊ TRÍ
        # ====================================================

        ma_vi_tri = (
            selected_slot.get(
                "mavitri"
            )
        )

        if ma_vi_tri is None:

            return json_response(
                {
                    "success": False,
                    "message":
                        (
                            "AI xác định được vị trí "
                            "nhưng thiếu mã vị trí"
                        ),
                    "ai": ai_result,
                    "occupancy":
                        occupancy_result,
                    "slot":
                        selected_slot
                },
                400
            )

        # ====================================================
        # BƯỚC 7
        # GHI LƯỢT GỬI XE VÀO SUPABASE
        #
        # QUAN TRỌNG:
        #
        # Không dùng:
        #
        #     ParkingService.vehicle_entry()
        #
        # vì hàm đó tự tìm slot.
        #
        # Dùng:
        #
        #     vehicle_entry_at_position()
        #
        # để sử dụng đúng vị trí AI xác định.
        # ====================================================

        parking_result = (
            ParkingService
            .vehicle_entry_at_position(
                bien_so,
                ma_loai_xe,
                ma_vi_tri
            )
        )

        if not parking_result["success"]:

            return json_response(
                {
                    "success": False,
                    "message":
                        parking_result.get(
                            "message",
                            "Không thể tạo lượt gửi xe"
                        ),

                    "ai":
                        ai_result,

                    "maloaixe":
                        ma_loai_xe,

                    "mavitri_ai":
                        ma_vi_tri,

                    "occupancy":
                        {
                            "mavitri":
                                ma_vi_tri,

                            "bbox":
                                selected_slot.get(
                                    "bbox"
                                ),

                            "trangthai":
                                selected_slot.get(
                                    "trangthai"
                                ),

                            "vehicle":
                                selected_slot.get(
                                    "vehicle"
                                )
                        },

                    "parking":
                        parking_result
                },
                400
            )

        # ====================================================
        # THÀNH CÔNG
        # ====================================================

        return json_response(
            {
                "success": True,

                "message":
                    "Xe vào bãi thành công",

                "ai":
                    ai_result.get(
                        "data",
                        {}
                    ),

                "loaixe":
                    vehicle_type_data,

                "maloaixe":
                    ma_loai_xe,

                "mavitri_ai":
                    ma_vi_tri,

                "occupancy":
                    {
                        "mavitri":
                            ma_vi_tri,

                        "bbox":
                            selected_slot.get(
                                "bbox"
                            ),

                        "trangthai":
                            selected_slot.get(
                                "trangthai"
                            ),

                        "vehicle":
                            selected_slot.get(
                                "vehicle"
                            )
                    },

                "parking":
                    parking_result
            },
            201
        )

    except Exception as e:

        return json_response(
            {
                "success": False,
                "message":
                    "Lỗi trong quá trình AI xe vào bãi",
                "error":
                    str(e)
            },
            500
        )

    finally:

        # ====================================================
        # XÓA FILE ẢNH TẠM
        # ====================================================

        if (
            temp_path
            and
            os.path.exists(
                temp_path
            )
        ):

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass


# ============================================================
# 5. AI EXIT
#
# Luồng:
#
# Camera
#   ↓
# AI nhận diện xe
#   ↓
# OCR biển số
#   ↓
# ParkingService.vehicle_exit()
#   ↓
# Tính phí
#   ↓
# Đóng LuotGuiXe
#   ↓
# Giải phóng vị trí
#
# ============================================================

@parking_bp.route(
    "/ai-exit",
    methods=["POST"]
)
def ai_vehicle_exit():

    if "image" not in request.files:

        return json_response(
            {
                "success": False,
                "message":
                    "Thiếu file ảnh"
            },
            400
        )

    image_file = request.files[
        "image"
    ]

    if image_file.filename == "":

        return json_response(
            {
                "success": False,
                "message":
                    "Tên file ảnh không hợp lệ"
            },
            400
        )

    temp_path = None

    try:

        # ====================================================
        # LƯU ẢNH TẠM
        # ====================================================

        suffix = os.path.splitext(
            image_file.filename
        )[1]

        if not suffix:
            suffix = ".jpg"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            image_file.save(
                temp_file.name
            )

            temp_path = temp_file.name

        # ====================================================
        # AI NHẬN DIỆN
        # ====================================================

        ai_result = (
            _get_parking_ai_service()
            .process_image(
                temp_path
            )
        )

        if not ai_result["success"]:

            return json_response(
                {
                    "success": False,
                    "message":
                        ai_result.get(
                            "message",
                            "AI không thể nhận diện xe"
                        ),
                    "ai":
                        ai_result
                },
                400
            )

        ai_data = (
            ai_result.get(
                "data",
                {}
            )
        )

        bien_so = (
            ai_data.get(
                "bienso"
            )
        )

        if not bien_so:

            return json_response(
                {
                    "success": False,
                    "message":
                        "AI không nhận diện được biển số",
                    "ai":
                        ai_result
                },
                400
            )

        # ====================================================
        # ĐÓNG LƯỢT GỬI XE
        # ====================================================

        parking_result = (
            ParkingService
            .vehicle_exit(
                bien_so
            )
        )

        if not parking_result["success"]:

            return json_response(
                {
                    "success": False,
                    "message":
                        parking_result.get(
                            "message",
                            "Không thể cho xe ra khỏi bãi"
                        ),

                    "ai":
                        ai_result,

                    "parking":
                        parking_result
                },
                400
            )

        # ====================================================
        # THÀNH CÔNG
        # ====================================================

        return json_response(
            {
                "success": True,

                "message":
                    "Xe ra khỏi bãi thành công",

                "ai":
                    ai_result.get(
                        "data",
                        {}
                    ),

                "parking":
                    parking_result
            },
            200
        )

    except Exception as e:

        return json_response(
            {
                "success": False,
                "message":
                    (
                        "Lỗi trong quá trình "
                        "AI xe ra khỏi bãi"
                    ),
                "error":
                    str(e)
            },
            500
        )

    finally:

        # ====================================================
        # XÓA FILE ẢNH TẠM
        # ====================================================

        if (
            temp_path
            and
            os.path.exists(
                temp_path
            )
        ):

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass


# ============================================================
# 6. AI STATUS
#
# Luồng:
#
# Camera
#   ↓
# Vehicle Detection
#   ↓
# Parking Occupancy Detection
#   ↓
# ParkingService.sync_ai_occupancy()
#   ↓
# Supabase
#
# AI STATUS KHÔNG:
#
#   - tạo LuotGuiXe
#   - đóng LuotGuiXe
#   - tính phí
#   - xác định xe vào / ra
#
# Nó chỉ đồng bộ trạng thái quan sát
# của AI với hệ thống.
#
# ============================================================

@parking_bp.route(
    "/ai-status",
    methods=["POST"]
)
def ai_parking_status():

    if "image" not in request.files:

        return json_response(
            {
                "success": False,
                "message":
                    "Thiếu file ảnh"
            },
            400
        )

    image_file = request.files[
        "image"
    ]

    if image_file.filename == "":

        return json_response(
            {
                "success": False,
                "message":
                    "Tên file ảnh không hợp lệ"
            },
            400
        )

    temp_path = None

    try:

        # ====================================================
        # LƯU ẢNH TẠM
        # ====================================================

        suffix = os.path.splitext(
            image_file.filename
        )[1]

        if not suffix:
            suffix = ".jpg"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            image_file.save(
                temp_file.name
            )

            temp_path = temp_file.name

        # ====================================================
        # AI NHẬN DIỆN TRẠNG THÁI BÃI
        # ====================================================

        ai_result = (
            _get_parking_occupancy_detector()
            .detect(
                temp_path
            )
        )

        if not ai_result["success"]:

            return json_response(
                ai_result,
                400
            )

        # ====================================================
        # ĐỒNG BỘ AI -> SUPABASE
        # ====================================================

        sync_result = (
            ParkingService
            .sync_ai_occupancy(
                ai_result
            )
        )

        if not sync_result["success"]:

            return json_response(
                {
                    "success": False,

                    "message":
                        (
                            "AI nhận diện thành công "
                            "nhưng đồng bộ thất bại"
                        ),

                    "ai":
                        ai_result,

                    "sync":
                        sync_result
                },
                400
            )

        # ====================================================
        # THÀNH CÔNG
        # ====================================================

        return json_response(
            {
                "success": True,

                "message":
                    (
                        "AI nhận diện và đồng bộ "
                        "trạng thái bãi xe thành công"
                    ),

                "ai":
                    ai_result,

                "sync":
                    sync_result
            },
            200
        )

    except Exception as e:

        return json_response(
            {
                "success": False,

                "message":
                    (
                        "Lỗi trong quá trình "
                        "AI đồng bộ trạng thái bãi xe"
                    ),

                "error":
                    str(e)
            },
            500
        )

    finally:

        # ====================================================
        # XÓA FILE ẢNH TẠM
        # ====================================================

        if (
            temp_path
            and
            os.path.exists(
                temp_path
            )
        ):

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass
