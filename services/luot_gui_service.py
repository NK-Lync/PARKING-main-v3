from database.supabase_client import supabase


class LuotGuiService:

    @staticmethod
    def get_all():
        response = (
            supabase
            .table("luotguixe")
            .select("*")
            .order("maluotgui")
            .execute()
        )

        return response.data

    @staticmethod
    def get_by_id(ma_luot_gui):
        response = (
            supabase
            .table("luotguixe")
            .select("*")
            .eq("maluotgui", ma_luot_gui)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def create(
        bien_so,
        ma_loai_xe,
        ma_vi_tri,
        thoi_gian_vao,
        thoi_gian_ra=None,
        tong_phi=0,
        tinh_trang=None,
        loai_ve=None
    ):
        data = {
            "bienso": bien_so,
            "maloaixe": ma_loai_xe,
            "mavitri": ma_vi_tri,
            "loaive": loai_ve if loai_ve is not None else "VE_LUOT",
            "thoigianvao": thoi_gian_vao,
            "tongphi": tong_phi
        }

        if thoi_gian_ra is not None:
            data["thoigianra"] = thoi_gian_ra

        if tinh_trang is not None:
            data["tinhtrang"] = tinh_trang

        response = (
            supabase
            .table("luotguixe")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def update(
        ma_luot_gui,
        bien_so,
        ma_loai_xe,
        ma_vi_tri,
        thoi_gian_vao,
        thoi_gian_ra,
        tong_phi,
        tinh_trang,
        loai_ve=None
    ):
        data = {
            "bienso": bien_so,
            "maloaixe": ma_loai_xe,
            "mavitri": ma_vi_tri,
            "loaive": loai_ve if loai_ve is not None else "VE_LUOT",
            "thoigianvao": thoi_gian_vao,
            "thoigianra": thoi_gian_ra,
            "tongphi": tong_phi,
            "tinhtrang": tinh_trang
        }

        response = (
            supabase
            .table("luotguixe")
            .update(data)
            .eq("maluotgui", ma_luot_gui)
            .execute()
        )

        return response.data

    @staticmethod
    def delete(ma_luot_gui):
        response = (
            supabase
            .table("luotguixe")
            .delete()
            .eq("maluotgui", ma_luot_gui)
            .execute()
        )

        return response.data