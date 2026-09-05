from database.supabase_client import supabase


class KhuVucService:

    # ============================================================
    # CRUD
    # ============================================================
    @staticmethod
    def get_all():
        response = (
            supabase
            .table("khuvuc")
            .select("*")
            .order("makhuvuc")
            .execute()
        )

        return response.data

    @staticmethod
    def get_by_id(ma_khu_vuc):
        response = (
            supabase
            .table("khuvuc")
            .select("*")
            .eq("makhuvuc", ma_khu_vuc)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def create(ten_khu_vuc, tong_so_vi_tri=0):
        data = {
            "tenkhuvuc": ten_khu_vuc,
            "tongsovitri": tong_so_vi_tri,
            "soxehientai": 0
        }

        response = (
            supabase
            .table("khuvuc")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def update(ma_khu_vuc, ten_khu_vuc, tong_so_vi_tri):
        data = {
            "tenkhuvuc": ten_khu_vuc,
            "tongsovitri": tong_so_vi_tri
        }

        response = (
            supabase
            .table("khuvuc")
            .update(data)
            .eq("makhuvuc", ma_khu_vuc)
            .execute()
        )

        return response.data

    @staticmethod
    def delete(ma_khu_vuc):
        response = (
            supabase
            .table("khuvuc")
            .delete()
            .eq("makhuvuc", ma_khu_vuc)
            .execute()
        )

        return response.data

    # ============================================================
    # NGHIỆP VỤ
    # ============================================================
    @staticmethod
    def lay_cho_trong():
        """
        Liệt kê số chỗ trống của từng khu vực.

        Vị trí đỗ (vitrido) được gắn với khu vực qua tên
        khu vực (tenkhuvuc). Phương thức này đếm số vị trí
        "Còn trống" theo từng tên khu vực rồi đối chiếu
        với bảng khuvuc.
        """
        khu_vucs = KhuVucService.get_all()

        if not khu_vucs:
            return []

        # Đếm vị trí trống theo tenkhuvuc.
        vi_tri_response = (
            supabase
            .table("vitrido")
            .select("tenkhuvuc, trangthai")
            .execute()
        )

        vi_tri_list = vi_tri_response.data or []

        so_trong = {}
        tong_vi_tri = {}

        for vi_tri in vi_tri_list:
            ten = vi_tri.get("tenkhuvuc")
            if not ten:
                continue

            tong_vi_tri[ten] = tong_vi_tri.get(ten, 0) + 1

            if vi_tri.get("trangthai") == "Còn trống":
                so_trong[ten] = so_trong.get(ten, 0) + 1

        result = []

        for khu_vuc in khu_vucs:
            ten = khu_vuc.get("tenkhuvuc")

            result.append({
                "makhuvuc": khu_vuc.get("makhuvuc"),
                "tenkhuvuc": ten,
                "tong_so_vi_tri": tong_vi_tri.get(ten, 0),
                "so_cho_trong": so_trong.get(ten, 0)
            })

        return result

    @staticmethod
    def cap_nhat_thong_tin():
        """
        Đồng bộ lại số xe hiện tại của từng khu vực
        dựa trên lượt gửi xe đang hoạt động (luotguixe).

        Cập nhật trực tiếp cột soxehientai của bảng khuvuc.
        """
        khu_vucs = KhuVucService.get_all()

        if not khu_vucs:
            return []

        # Số xe đang gửi theo tenkhuvuc (thông qua vitrido).
        luot_response = (
            supabase
            .table("luotguixe")
            .select("mavitri")
            .eq("tinhtrang", "Đang gửi")
            .execute()
        )

        luot_list = luot_response.data or []

        ma_vi_tri_active = {
            luot["mavitri"]
            for luot in luot_list
            if luot.get("mavitri") is not None
        }

        vi_tri_response = (
            supabase
            .table("vitrido")
            .select("mavitri, tenkhuvuc")
            .execute()
        )

        vi_tri_list = vi_tri_response.data or []

        so_xe = {}

        for vi_tri in vi_tri_list:
            if vi_tri.get("mavitri") in ma_vi_tri_active:
                ten = vi_tri.get("tenkhuvuc")
                if ten:
                    so_xe[ten] = so_xe.get(ten, 0) + 1

        result = []

        for khu_vuc in khu_vucs:
            ma = khu_vuc.get("makhuvuc")
            ten = khu_vuc.get("tenkhuvuc")
            xe_hien_tai = so_xe.get(ten, 0)

            supabase.table("khuvuc").update({
                "soxehientai": xe_hien_tai
            }).eq("makhuvuc", ma).execute()

            result.append({
                "makhuvuc": ma,
                "tenkhuvuc": ten,
                "soxehientai": xe_hien_tai
            })

        return result
