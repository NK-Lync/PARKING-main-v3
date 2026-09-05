from database.supabase_client import supabase


class ViTriService:

    @staticmethod
    def get_all():
        response = (
            supabase
            .table("vitrido")
            .select("*")
            .order("mavitri")
            .execute()
        )

        return response.data

    @staticmethod
    def get_by_id(ma_vi_tri):
        response = (
            supabase
            .table("vitrido")
            .select("*")
            .eq("mavitri", ma_vi_tri)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def create(ten_khu_vuc, trang_thai=None):
        data = {
            "tenkhuvuc": ten_khu_vuc
        }

        if trang_thai is not None:
            data["trangthai"] = trang_thai

        response = (
            supabase
            .table("vitrido")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def update(ma_vi_tri, ten_khu_vuc, trang_thai):
        data = {
            "tenkhuvuc": ten_khu_vuc,
            "trangthai": trang_thai
        }

        response = (
            supabase
            .table("vitrido")
            .update(data)
            .eq("mavitri", ma_vi_tri)
            .execute()
        )

        return response.data

    @staticmethod
    def delete(ma_vi_tri):
        response = (
            supabase
            .table("vitrido")
            .delete()
            .eq("mavitri", ma_vi_tri)
            .execute()
        )

        return response.data