from flask import Blueprint, request, jsonify
from services.loai_xe_service import LoaiXeService


loai_xe_bp = Blueprint("loai_xe", __name__)


# GET /api/loaixe
@loai_xe_bp.route("/api/loaixe", methods=["GET"])
def get_all_loai_xe():
    try:
        data = LoaiXeService.get_all()

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# GET /api/loaixe/<id>
@loai_xe_bp.route("/api/loaixe/<int:ma_loai_xe>", methods=["GET"])
def get_loai_xe(ma_loai_xe):
    try:
        data = LoaiXeService.get_by_id(ma_loai_xe)

        if data is None:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy loại xe"
            }), 404

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# POST /api/loaixe
@loai_xe_bp.route("/api/loaixe", methods=["POST"])
def create_loai_xe():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }), 400

        ten_loai_xe = data.get("tenloaixe")
        don_gia = data.get("dongia")

        if not ten_loai_xe or don_gia is None:
            return jsonify({
                "success": False,
                "message": "Thiếu tenloaixe hoặc dongia"
            }), 400

        result = LoaiXeService.create(
            ten_loai_xe,
            don_gia
        )

        return jsonify({
            "success": True,
            "message": "Thêm loại xe thành công",
            "data": result
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# PUT /api/loaixe/<id>
@loai_xe_bp.route("/api/loaixe/<int:ma_loai_xe>", methods=["PUT"])
def update_loai_xe(ma_loai_xe):
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }), 400

        ten_loai_xe = data.get("tenloaixe")
        don_gia = data.get("dongia")

        if not ten_loai_xe or don_gia is None:
            return jsonify({
                "success": False,
                "message": "Thiếu tenloaixe hoặc dongia"
            }), 400

        result = LoaiXeService.update(
            ma_loai_xe,
            ten_loai_xe,
            don_gia
        )

        if not result:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy loại xe"
            }), 404

        return jsonify({
            "success": True,
            "message": "Cập nhật loại xe thành công",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# DELETE /api/loaixe/<id>
@loai_xe_bp.route("/api/loaixe/<int:ma_loai_xe>", methods=["DELETE"])
def delete_loai_xe(ma_loai_xe):
    try:
        result = LoaiXeService.delete(ma_loai_xe)

        if not result:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy loại xe"
            }), 404

        return jsonify({
            "success": True,
            "message": "Xóa loại xe thành công",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500