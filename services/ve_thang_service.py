from database.supabase_client import supabase


class VeThangService:

    @staticmethod
    def get_all():
        response = (
            supabase
            .table("vethang")
            .select("*")
            .order("mave")
            .execute()
        )

        return response.data

    @staticmethod
    def get_by_id(ma_ve):
        response = (
            supabase
            .table("vethang")
            .select("*")
            .eq("mave", ma_ve)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def create(
        bien_so,
        ngay_het_han,
        trang_thai=None,
        ten_khach_hang=None,
        ma_loai_xe=None,
        ngay_dang_ky=None
    ):
        data = {
            "bienso": bien_so,
            "ngayhethan": ngay_het_han
        }

        if trang_thai is not None:
            data["trangthai"] = trang_thai

        if ten_khach_hang is not None:
            data["tenkhachhang"] = ten_khach_hang

        if ma_loai_xe is not None:
            data["maloaixe"] = ma_loai_xe

        if ngay_dang_ky is not None:
            data["ngaydangky"] = ngay_dang_ky

        response = (
            supabase
            .table("vethang")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def update(
        ma_ve,
        bien_so,
        ngay_het_han,
        trang_thai,
        ten_khach_hang=None,
        ma_loai_xe=None,
        ngay_dang_ky=None
    ):
        data = {
            "bienso": bien_so,
            "ngayhethan": ngay_het_han,
            "trangthai": trang_thai
        }

        if ten_khach_hang is not None:
            data["tenkhachhang"] = ten_khach_hang

        if ma_loai_xe is not None:
            data["maloaixe"] = ma_loai_xe

        if ngay_dang_ky is not None:
            data["ngaydangky"] = ngay_dang_ky

        response = (
            supabase
            .table("vethang")
            .update(data)
            .eq("mave", ma_ve)
            .execute()
        )

        return response.data

    @staticmethod
    def delete(ma_ve):
        response = (
            supabase
            .table("vethang")
            .delete()
            .eq("mave", ma_ve)
            .execute()
        )

        return response.data