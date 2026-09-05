from flask import Blueprint, request, Response
import json

from services.khu_vuc_service import KhuVucService


khu_vuc_bp = Blueprint("khu_vuc", __name__)


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


# GET tất cả khu vực
@khu_vuc_bp.route("/api/khuvuc", methods=["GET"])
def get_all_khu_vuc():
    try:
        data = KhuVucService.get_all()

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# GET khu vực theo ID
@khu_vuc_bp.route("/api/khuvuc/<int:ma_khu_vuc>", methods=["GET"])
def get_khu_vuc(ma_khu_vuc):
    try:
        data = KhuVucService.get_by_id(ma_khu_vuc)

        if data is None:
            return json_response({
                "success": False,
                "message": "Không tìm thấy khu vực"
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


# POST thêm khu vực
@khu_vuc_bp.route("/api/khuvuc", methods=["POST"])
def create_khu_vuc():
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        ten_khu_vuc = data.get("tenkhuvuc")
        tong_so_vi_tri = data.get("tongsovitri", 0)

        if not ten_khu_vuc:
            return json_response({
                "success": False,
                "message": "Thiếu tenkhuvuc"
            }, 400)

        result = KhuVucService.create(
            ten_khu_vuc,
            tong_so_vi_tri
        )

        return json_response({
            "success": True,
            "message": "Thêm khu vực thành công",
            "data": result
        }, 201)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# PUT cập nhật khu vực
@khu_vuc_bp.route("/api/khuvuc/<int:ma_khu_vuc>", methods=["PUT"])
def update_khu_vuc(ma_khu_vuc):
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        ten_khu_vuc = data.get("tenkhuvuc")
        tong_so_vi_tri = data.get("tongsovitri")

        if not ten_khu_vuc:
            return json_response({
                "success": False,
                "message": "Thiếu tenkhuvuc"
            }, 400)

        if tong_so_vi_tri is None:
            return json_response({
                "success": False,
                "message": "Thiếu tongsovitri"
            }, 400)

        result = KhuVucService.update(
            ma_khu_vuc,
            ten_khu_vuc,
            tong_so_vi_tri
        )

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy khu vực"
            }, 404)

        return json_response({
            "success": True,
            "message": "Cập nhật khu vực thành công",
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# DELETE xóa khu vực
@khu_vuc_bp.route("/api/khuvuc/<int:ma_khu_vuc>", methods=["DELETE"])
def delete_khu_vuc(ma_khu_vuc):
    try:
        result = KhuVucService.delete(ma_khu_vuc)

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy khu vực"
            }, 404)

        return json_response({
            "success": True,
            "message": "Xóa khu vực thành công",
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# GET số chỗ trống của các khu vực
@khu_vuc_bp.route("/api/khuvuc/cho-trong", methods=["GET"])
def lay_cho_trong():
    try:
        data = KhuVucService.lay_cho_trong()

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST đồng bộ số xe hiện tại
@khu_vuc_bp.route("/api/khuvuc/cap-nhat", methods=["POST"])
def cap_nhat_thong_tin():
    try:
        data = KhuVucService.cap_nhat_thong_tin()

        return json_response({
            "success": True,
            "message": "Cập nhật số xe hiện tại thành công",
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)
