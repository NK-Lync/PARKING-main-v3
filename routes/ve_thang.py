from flask import Blueprint, request, Response
import json

from services.ve_thang_service import VeThangService


ve_thang_bp = Blueprint("ve_thang", __name__)


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


# GET tất cả vé tháng
@ve_thang_bp.route("/api/vethang", methods=["GET"])
def get_all_ve_thang():
    try:
        data = VeThangService.get_all()

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# GET vé tháng theo ID
@ve_thang_bp.route("/api/vethang/<int:ma_ve>", methods=["GET"])
def get_ve_thang(ma_ve):
    try:
        data = VeThangService.get_by_id(ma_ve)

        if data is None:
            return json_response({
                "success": False,
                "message": "Không tìm thấy vé tháng"
            }, 404)

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST thêm vé tháng
@ve_thang_bp.route("/api/vethang", methods=["POST"])
def create_ve_thang():
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        bien_so = data.get("bienso")
        ngay_het_han = data.get("ngayhethan")
        trang_thai = data.get("trangthai")

        if not bien_so:
            return json_response({
                "success": False,
                "message": "Thiếu bienso"
            }, 400)

        if not ngay_het_han:
            return json_response({
                "success": False,
                "message": "Thiếu ngayhethan"
            }, 400)

        result = VeThangService.create(
            bien_so,
            ngay_het_han,
            trang_thai
        )

        return json_response({
            "success": True,
            "message": "Thêm vé tháng thành công",
            "data": result
        }, 201)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# PUT cập nhật vé tháng
@ve_thang_bp.route("/api/vethang/<int:ma_ve>", methods=["PUT"])
def update_ve_thang(ma_ve):
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        bien_so = data.get("bienso")
        ngay_het_han = data.get("ngayhethan")
        trang_thai = data.get("trangthai")

        if not bien_so:
            return json_response({
                "success": False,
                "message": "Thiếu bienso"
            }, 400)

        if not ngay_het_han:
            return json_response({
                "success": False,
                "message": "Thiếu ngayhethan"
            }, 400)

        if trang_thai is None:
            return json_response({
                "success": False,
                "message": "Thiếu trangthai"
            }, 400)

        result = VeThangService.update(
            ma_ve,
            bien_so,
            ngay_het_han,
            trang_thai
        )

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy vé tháng"
            }, 404)

        return json_response({
            "success": True,
            "message": "Cập nhật vé tháng thành công",
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# DELETE xóa vé tháng
@ve_thang_bp.route("/api/vethang/<int:ma_ve>", methods=["DELETE"])
def delete_ve_thang(ma_ve):
    try:
        result = VeThangService.delete(ma_ve)

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy vé tháng"
            }, 404)

        return json_response({
            "success": True,
            "message": "Xóa vé tháng thành công",
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)