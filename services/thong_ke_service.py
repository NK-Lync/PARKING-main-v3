from collections import defaultdict
from datetime import datetime

from database.supabase_client import supabase


class ThongKeService:

    # ============================================================
    # THỐNG KÊ LƯU LƯỢNG XE
    # ============================================================
    @staticmethod
    def lay_luu_luong(ngay=None):
        """
        Thống kê số lượt xe vào theo từng giờ trong ngày.

        Tham số:
            ngay (str): ngày cần thống kê dạng "YYYY-MM-DD".
                        Nếu None thì thống kê tất cả.

        Trả về:
            dict:
                {
                    "tong_luot": ...,
                    "theo_gio": {0: ..., 1: ..., ..., 23: ...}
                }
        """
        query = supabase.table("luotguixe").select("thoigianvao")

        if ngay is not None:
            query = query.gte("thoigianvao", f"{ngay}T00:00:00")

        response = query.execute()

        luot_list = response.data or []

        theo_gio = defaultdict(int)

        for luot in luot_list:
            thoi_gian_vao = luot.get("thoigianvao")

            if not thoi_gian_vao:
                continue

            try:
                dt = datetime.fromisoformat(
                    thoi_gian_vao.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                continue

            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)

            theo_gio[dt.hour] += 1

        # Đảm bảo đủ 24 giờ.
        full = {gio: theo_gio.get(gio, 0) for gio in range(24)}

        return {
            "tong_luot": sum(full.values()),
            "theo_gio": full
        }

    # ============================================================
    # THỐNG KÊ DOANH THU
    # ============================================================
    @staticmethod
    def lay_doanh_thu(ngay=None):
        """
        Tính tổng doanh thu từ các lượt gửi xe đã trả.

        Tham số:
            ngay (str): ngày cần thống kê dạng "YYYY-MM-DD".
                        Nếu None thì thống kê tất cả.

        Trả về:
            dict:
                {
                    "tong_doanh_thu": ...,
                    "so_luot_da_tra": ...
                }
        """
        query = (
            supabase
            .table("luotguixe")
            .select("tongphi, thoigianra")
            .eq("tinhtrang", "Đã trả")
        )

        if ngay is not None:
            query = query.gte("thoigianra", f"{ngay}T00:00:00")

        response = query.execute()

        luot_list = response.data or []

        tong_doanh_thu = 0

        for luot in luot_list:
            tong_phi = luot.get("tongphi")

            if tong_phi is None:
                continue

            try:
                tong_doanh_thu += float(tong_phi)
            except (ValueError, TypeError):
                continue

        return {
            "tong_doanh_thu": tong_doanh_thu,
            "so_luot_da_tra": len(luot_list)
        }

    # ============================================================
    # TỔNG HỢP DỮ LIỆU PHÂN TÍCH (CHO GENAI)
    # ============================================================
    @staticmethod
    def du_lieu_phan_tich():
        """
        Gom toàn bộ số liệu nghiệp vụ để cung cấp cho
        HeThongAI (GenAI) phân tích.

        Dữ liệu trả về chỉ là các con số đã được hệ thống
        tổng hợp. HeThongAI chỉ phân tích, không tự tạo số.
        """
        luu_luong = ThongKeService.lay_luu_luong()
        doanh_thu = ThongKeService.lay_doanh_thu()

        # Số xe đang gửi hiện tại.
        active_response = (
            supabase
            .table("luotguixe")
            .select("maluotgui")
            .eq("tinhtrang", "Đang gửi")
            .execute()
        )

        # Tổng số vị trí.
        vi_tri_response = (
            supabase
            .table("vitrido")
            .select("mavitri")
            .execute()
        )

        # Số vé tháng còn hiệu lực.
        ve_thang_response = (
            supabase
            .table("vethang")
            .select("mave")
            .eq("trangthai", True)
            .execute()
        )

        return {
            "tong_luot_gui": luu_luong["tong_luot"],
            "luu_luong_theo_gio": luu_luong["theo_gio"],
            "tong_doanh_thu": doanh_thu["tong_doanh_thu"],
            "so_luot_da_tra": doanh_thu["so_luot_da_tra"],
            "so_xe_dang_gui": len(active_response.data or []),
            "tong_so_vi_tri": len(vi_tri_response.data or []),
            "so_ve_thang_hieu_luc": len(ve_thang_response.data or [])
        }
