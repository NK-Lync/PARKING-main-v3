from flask import Blueprint, request, jsonify
from services.luot_gui_service import LuotGuiService


luot_gui_bp = Blueprint("luot_gui", __name__)


@luot_gui_bp.route("/api/luotguixe", methods=["GET"])
def get_all_luot_gui():
    try:
        data = LuotGuiService.get_all()

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@luot_gui_bp.route("/api/luotguixe/<int:ma_luot_gui>", methods=["GET"])
def get_luot_gui(ma_luot_gui):
    try:
        data = LuotGuiService.get_by_id(ma_luot_gui)

        if data is None:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy lượt gửi xe"
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


@luot_gui_bp.route("/api/luotguixe", methods=["POST"])
def create_luot_gui():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }), 400

        bien_so = data.get("bienso")
        ma_loai_xe = data.get("maloaixe")
        ma_vi_tri = data.get("mavitri")
        thoi_gian_vao = data.get("thoigianvao")
        thoi_gian_ra = data.get("thoigianra")
        tong_phi = data.get("tongphi", 0)
        tinh_trang = data.get("tinhtrang")

        if not bien_so:
            return jsonify({
                "success": False,
                "message": "Thiếu bienso"
            }), 400

        if ma_loai_xe is None:
            return jsonify({
                "success": False,
                "message": "Thiếu maloaixe"
            }), 400

        if ma_vi_tri is None:
            return jsonify({
                "success": False,
                "message": "Thiếu mavitri"
            }), 400

        if not thoi_gian_vao:
            return jsonify({
                "success": False,
                "message": "Thiếu thoigianvao"
            }), 400

        loai_ve = data.get("loaive")

        result = LuotGuiService.create(
            bien_so,
            ma_loai_xe,
            ma_vi_tri,
            thoi_gian_vao,
            thoi_gian_ra,
            tong_phi,
            tinh_trang,
            loai_ve
        )

        return jsonify({
            "success": True,
            "message": "Thêm lượt gửi xe thành công",
            "data": result
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@luot_gui_bp.route("/api/luotguixe/<int:ma_luot_gui>", methods=["PUT"])
def update_luot_gui(ma_luot_gui):
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }), 400

        bien_so = data.get("bienso")
        ma_loai_xe = data.get("maloaixe")
        ma_vi_tri = data.get("mavitri")
        thoi_gian_vao = data.get("thoigianvao")
        thoi_gian_ra = data.get("thoigianra")
        tong_phi = data.get("tongphi", 0)
        tinh_trang = data.get("tinhtrang")

        if not bien_so or ma_loai_xe is None or ma_vi_tri is None:
            return jsonify({
                "success": False,
                "message": "Thiếu thông tin lượt gửi xe"
            }), 400

        if not thoi_gian_vao:
            return jsonify({
                "success": False,
                "message": "Thiếu thoigianvao"
            }), 400

        if tinh_trang is None:
            return jsonify({
                "success": False,
                "message": "Thiếu tinhtrang"
            }), 400

        loai_ve = data.get("loaive")

        result = LuotGuiService.update(
            ma_luot_gui,
            bien_so,
            ma_loai_xe,
            ma_vi_tri,
            thoi_gian_vao,
            thoi_gian_ra,
            tong_phi,
            tinh_trang,
            loai_ve
        )

        if not result:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy lượt gửi xe"
            }), 404

        return jsonify({
            "success": True,
            "message": "Cập nhật lượt gửi xe thành công",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@luot_gui_bp.route("/api/luotguixe/<int:ma_luot_gui>", methods=["DELETE"])
def delete_luot_gui(ma_luot_gui):
    try:
        result = LuotGuiService.delete(ma_luot_gui)

        if not result:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy lượt gửi xe"
            }), 404

        return jsonify({
            "success": True,
            "message": "Xóa lượt gửi xe thành công",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500