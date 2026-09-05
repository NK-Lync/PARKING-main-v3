from database.supabase_client import supabase


class LoaiXeService:

    @staticmethod
    def get_all():
        response = (
            supabase
            .table("loaixe")
            .select("*")
            .order("maloaixe")
            .execute()
        )

        return response.data

    @staticmethod
    def get_by_id(ma_loai_xe):
        response = (
            supabase
            .table("loaixe")
            .select("*")
            .eq("maloaixe", ma_loai_xe)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def create(ten_loai_xe, don_gia):
        data = {
            "tenloaixe": ten_loai_xe,
            "dongia": don_gia
        }

        response = (
            supabase
            .table("loaixe")
            .insert(data)
            .execute()
        )

        return response.data

    @staticmethod
    def update(ma_loai_xe, ten_loai_xe, don_gia):
        data = {
            "tenloaixe": ten_loai_xe,
            "dongia": don_gia
        }

        response = (
            supabase
            .table("loaixe")
            .update(data)
            .eq("maloaixe", ma_loai_xe)
            .execute()
        )

        return response.data

    @staticmethod
    def delete(ma_loai_xe):
        response = (
            supabase
            .table("loaixe")
            .delete()
            .eq("maloaixe", ma_loai_xe)
            .execute()
        )

        return response.data