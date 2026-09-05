import hashlib

from database.supabase_client import supabase


class TaiKhoanService:

    # ============================================================
    # MÃ HÓA MẬT KHẨU
    # ============================================================
    @staticmethod
    def _ma_hoa_mat_khau(mat_khau):
        return hashlib.sha256(
            mat_khau.encode("utf-8")
        ).hexdigest()

    # ============================================================
    # CRUD
    # ============================================================
    @staticmethod
    def get_all():
        response = (
            supabase
            .table("taikhoan")
            .select("*")
            .order("mand")
            .execute()
        )

        return response.data

    @staticmethod
    def get_by_id(ma_nd):
        response = (
            supabase
            .table("taikhoan")
            .select("*")
            .eq("mand", ma_nd)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def get_by_ten_dang_nhap(ten_dang_nhap):
        response = (
            supabase
            .table("taikhoan")
            .select("*")
            .eq("tendangnhap", ten_dang_nhap)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def create(
        ten_dang_nhap,
        mat_khau,
        vai_tro,
        trang_thai=True,
        email=None,
        so_dien_thoai=None
    ):
        data = {
            "tendangnhap": ten_dang_nhap,
            "matkhau": TaiKhoanService._ma_hoa_mat_khau(mat_khau),
            "vaitro": vai_tro,
            "trangthai": trang_thai
        }

        if email is not None:
            data["email"] = email

        if so_dien_thoai is not None:
            data["sodienthoai"] = so_dien_thoai

        response = (
            supabase
            .table("taikhoan")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def update(
        ma_nd,
        ten_dang_nhap,
        vai_tro,
        trang_thai,
        mat_khau=None,
        email=None,
        so_dien_thoai=None
    ):
        data = {
            "tendangnhap": ten_dang_nhap,
            "vaitro": vai_tro,
            "trangthai": trang_thai
        }

        if mat_khau is not None:
            data["matkhau"] = (
                TaiKhoanService._ma_hoa_mat_khau(mat_khau)
            )

        if email is not None:
            data["email"] = email

        if so_dien_thoai is not None:
            data["sodienthoai"] = so_dien_thoai

        response = (
            supabase
            .table("taikhoan")
            .update(data)
            .eq("mand", ma_nd)
            .execute()
        )

        return response.data

    @staticmethod
    def delete(ma_nd):
        response = (
            supabase
            .table("taikhoan")
            .delete()
            .eq("mand", ma_nd)
            .execute()
        )

        return response.data

    # ============================================================
    # XÁC THỰC
    # ============================================================
    @staticmethod
    def dang_nhap(ten_dang_nhap, mat_khau):
        """
        Kiểm tra tên đăng nhập và mật khẩu.

        Trả về:
            success=True  → tài khoản hợp lệ và đang hoạt động
            success=False → sai mật khẩu / tài khoản bị khóa
        """
        tai_khoan = TaiKhoanService.get_by_ten_dang_nhap(
            ten_dang_nhap
        )

        if tai_khoan is None:
            return {
                "success": False,
                "message": "Tên đăng nhập không tồn tại"
            }

        mat_khau_ma_hoa = (
            TaiKhoanService._ma_hoa_mat_khau(mat_khau)
        )

        if tai_khoan["matkhau"] != mat_khau_ma_hoa:
            return {
                "success": False,
                "message": "Mật khẩu không đúng"
            }

        if tai_khoan.get("trangthai") is not True:
            return {
                "success": False,
                "message": "Tài khoản đã bị khóa"
            }

        return {
            "success": True,
            "message": "Đăng nhập thành công",
            "data": {
                "mand": tai_khoan["mand"],
                "tendangnhap": tai_khoan["tendangnhap"],
                "vaitro": tai_khoan["vaitro"]
            }
        }

    @staticmethod
    def dang_xuat(ma_nd):
        # Trong kiến trúc không dùng session/token,
        # đăng xuất đơn thuần là xác nhận kết thúc phiên làm việc.
        return {
            "success": True,
            "message": "Đăng xuất thành công",
            "data": {"mand": ma_nd}
        }
