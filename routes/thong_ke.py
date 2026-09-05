from flask import Blueprint, request, Response
import json

from services.thong_ke_service import ThongKeService


thong_ke_bp = Blueprint("thong_ke", __name__)


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


# GET thống kê lưu lượng xe
@thong_ke_bp.route("/api/thongke/luu-luong", methods=["GET"])
def lay_luu_luong():
    try:
        ngay = request.args.get("ngay")

        data = ThongKeService.lay_luu_luong(ngay)

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# GET thống kê doanh thu
@thong_ke_bp.route("/api/thongke/doanh-thu", methods=["GET"])
def lay_doanh_thu():
    try:
        ngay = request.args.get("ngay")

        data = ThongKeService.lay_doanh_thu(ngay)

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# GET tổng hợp dữ liệu phân tích
@thong_ke_bp.route("/api/thongke/phan-tich", methods=["GET"])
def du_lieu_phan_tich():
    try:
        data = ThongKeService.du_lieu_phan_tich()

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)
