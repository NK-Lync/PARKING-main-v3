from flask import Blueprint, request, jsonify, Response
import json

from services.vi_tri_service import ViTriService


vi_tri_bp = Blueprint("vi_tri", __name__)


# =========================================================
# Hàm tạo JSON response UTF-8
# =========================================================
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


# =========================================================
# GET tất cả vị trí
# =========================================================
@vi_tri_bp.route("/api/vitrido", methods=["GET"])
def get_all_vi_tri():
    try:
        data = ViTriService.get_all()

        return json_response({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# GET vị trí theo ID
# =========================================================
@vi_tri_bp.route("/api/vitrido/<int:ma_vi_tri>", methods=["GET"])
def get_vi_tri(ma_vi_tri):
    try:
        data = ViTriService.get_by_id(ma_vi_tri)

        if data is None:
            return json_response({
                "success": False,
                "message": "Không tìm thấy vị trí đỗ"
            }), 404

        print("DEBUG data:", data)
        print("DEBUG trangthai:", repr(data["trangthai"]))

        return json_response({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# POST thêm vị trí
# =========================================================
@vi_tri_bp.route("/api/vitrido", methods=["POST"])
def create_vi_tri():
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }), 400

        ten_khu_vuc = data.get("tenkhuvuc")
        trang_thai = data.get("trangthai")

        if not ten_khu_vuc:
            return json_response({
                "success": False,
                "message": "Thiếu tenkhuvuc"
            }), 400

        result = ViTriService.create(
            ten_khu_vuc,
            trang_thai
        )

        return json_response({
            "success": True,
            "message": "Thêm vị trí đỗ thành công",
            "data": result
        }), 201

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# PUT cập nhật vị trí
# =========================================================
@vi_tri_bp.route("/api/vitrido/<int:ma_vi_tri>", methods=["PUT"])
def update_vi_tri(ma_vi_tri):
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }), 400

        ten_khu_vuc = data.get("tenkhuvuc")
        trang_thai = data.get("trangthai")

        if not ten_khu_vuc or trang_thai is None:
            return json_response({
                "success": False,
                "message": "Thiếu tenkhuvuc hoặc trangthai"
            }), 400

        result = ViTriService.update(
            ma_vi_tri,
            ten_khu_vuc,
            trang_thai
        )

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy vị trí đỗ"
            }), 404

        return json_response({
            "success": True,
            "message": "Cập nhật vị trí đỗ thành công",
            "data": result
        }), 200

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# DELETE xóa vị trí
# =========================================================
@vi_tri_bp.route("/api/vitrido/<int:ma_vi_tri>", methods=["DELETE"])
def delete_vi_tri(ma_vi_tri):
    try:
        result = ViTriService.delete(ma_vi_tri)

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy vị trí đỗ"
            }), 404

        return json_response({
            "success": True,
            "message": "Xóa vị trí đỗ thành công",
            "data": result
        }), 200

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }), 500