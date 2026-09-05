from flask import Blueprint, request, Response
import json

from ai.he_thong_ai import HeThongAI
from services.thong_ke_service import ThongKeService


he_thong_ai_bp = Blueprint("he_thong_ai", __name__)


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


he_thong_ai = HeThongAI()


# POST sinh báo cáo lưu lượng
@he_thong_ai_bp.route("/api/ai/bao-cao-luu-luong", methods=["POST"])
def sinh_bao_cao_luu_luong():
    try:
        data = ThongKeService.du_lieu_phan_tich()

        result = he_thong_ai.sinh_bao_cao_luu_luong(data)

        return json_response({
            "success": True,
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST phân tích giờ cao điểm
@he_thong_ai_bp.route("/api/ai/gio-cao-diem", methods=["POST"])
def phan_tich_gio_cao_diem():
    try:
        data = ThongKeService.du_lieu_phan_tich()

        result = he_thong_ai.phan_tich_gio_cao_diem(data)

        return json_response({
            "success": True,
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST gợi ý bố trí nhân sự
@he_thong_ai_bp.route("/api/ai/goi-y-nhan-su", methods=["POST"])
def goi_y_bo_tri_nhan_su():
    try:
        data = ThongKeService.du_lieu_phan_tich()

        result = he_thong_ai.goi_y_bo_tri_nhan_su(data)

        return json_response({
            "success": True,
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST hỏi đáp dữ liệu
@he_thong_ai_bp.route("/api/ai/hoi-dap", methods=["POST"])
def hoi_dap_du_lieu():
    try:
        body = request.get_json()

        if not body:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        question = body.get("cau_hoi")

        if not question:
            return json_response({
                "success": False,
                "message": "Thiếu cau_hoi"
            }, 400)

        context = ThongKeService.du_lieu_phan_tich()

        result = he_thong_ai.hoi_dap_du_lieu(
            question,
            context
        )

        return json_response({
            "success": True,
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)
