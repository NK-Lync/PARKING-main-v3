from flask import Blueprint, request, Response
import json

from services.tai_khoan_service import TaiKhoanService


tai_khoan_bp = Blueprint("tai_khoan", __name__)


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


# GET tất cả tài khoản
@tai_khoan_bp.route("/api/taikhoan", methods=["GET"])
def get_all_tai_khoan():
    try:
        data = TaiKhoanService.get_all()

        return json_response({
            "success": True,
            "data": data
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# GET tài khoản theo ID
@tai_khoan_bp.route("/api/taikhoan/<int:ma_nd>", methods=["GET"])
def get_tai_khoan(ma_nd):
    try:
        data = TaiKhoanService.get_by_id(ma_nd)

        if data is None:
            return json_response({
                "success": False,
                "message": "Không tìm thấy tài khoản"
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


# POST thêm tài khoản
@tai_khoan_bp.route("/api/taikhoan", methods=["POST"])
def create_tai_khoan():
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        ten_dang_nhap = data.get("tendangnhap")
        mat_khau = data.get("matkhau")
        vai_tro = data.get("vaitro")
        trang_thai = data.get("trangthai", True)
        email = data.get("email")
        so_dien_thoai = data.get("sodienthoai")

        if not ten_dang_nhap:
            return json_response({
                "success": False,
                "message": "Thiếu tendangnhap"
            }, 400)

        if not mat_khau:
            return json_response({
                "success": False,
                "message": "Thiếu matkhau"
            }, 400)

        if not vai_tro:
            return json_response({
                "success": False,
                "message": "Thiếu vaitro"
            }, 400)

        result = TaiKhoanService.create(
            ten_dang_nhap,
            mat_khau,
            vai_tro,
            trang_thai,
            email,
            so_dien_thoai
        )

        return json_response({
            "success": True,
            "message": "Thêm tài khoản thành công",
            "data": result
        }, 201)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# PUT cập nhật tài khoản
@tai_khoan_bp.route("/api/taikhoan/<int:ma_nd>", methods=["PUT"])
def update_tai_khoan(ma_nd):
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        ten_dang_nhap = data.get("tendangnhap")
        vai_tro = data.get("vaitro")
        trang_thai = data.get("trangthai")
        mat_khau = data.get("matkhau")
        email = data.get("email")
        so_dien_thoai = data.get("sodienthoai")

        if not ten_dang_nhap:
            return json_response({
                "success": False,
                "message": "Thiếu tendangnhap"
            }, 400)

        if not vai_tro:
            return json_response({
                "success": False,
                "message": "Thiếu vaitro"
            }, 400)

        if trang_thai is None:
            return json_response({
                "success": False,
                "message": "Thiếu trangthai"
            }, 400)

        result = TaiKhoanService.update(
            ma_nd,
            ten_dang_nhap,
            vai_tro,
            trang_thai,
            mat_khau,
            email,
            so_dien_thoai
        )

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy tài khoản"
            }, 404)

        return json_response({
            "success": True,
            "message": "Cập nhật tài khoản thành công",
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# DELETE xóa tài khoản
@tai_khoan_bp.route("/api/taikhoan/<int:ma_nd>", methods=["DELETE"])
def delete_tai_khoan(ma_nd):
    try:
        result = TaiKhoanService.delete(ma_nd)

        if not result:
            return json_response({
                "success": False,
                "message": "Không tìm thấy tài khoản"
            }, 404)

        return json_response({
            "success": True,
            "message": "Xóa tài khoản thành công",
            "data": result
        }, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST đăng nhập
@tai_khoan_bp.route("/api/taikhoan/dang-nhap", methods=["POST"])
def dang_nhap():
    try:
        data = request.get_json()

        if not data:
            return json_response({
                "success": False,
                "message": "Dữ liệu JSON không hợp lệ"
            }, 400)

        ten_dang_nhap = data.get("tendangnhap")
        mat_khau = data.get("matkhau")

        if not ten_dang_nhap or not mat_khau:
            return json_response({
                "success": False,
                "message": "Thiếu tendangnhap hoặc matkhau"
            }, 400)

        result = TaiKhoanService.dang_nhap(
            ten_dang_nhap,
            mat_khau
        )

        if not result["success"]:
            return json_response(result, 401)

        return json_response(result, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)


# POST đăng xuất
@tai_khoan_bp.route("/api/taikhoan/dang-xuat", methods=["POST"])
def dang_xuat():
    try:
        data = request.get_json(silent=True) or {}

        ma_nd = data.get("mand")

        if ma_nd is None:
            return json_response({
                "success": False,
                "message": "Thiếu mand"
            }, 400)

        result = TaiKhoanService.dang_xuat(ma_nd)

        return json_response(result, 200)

    except Exception as e:
        return json_response({
            "success": False,
            "message": str(e)
        }, 500)
