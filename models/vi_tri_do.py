class ViTriDo:
    def __init__(
        self,
        maViTri=None,
        maKhuVuc=None,
        trangThai=None
    ):
        self.maViTri = maViTri
        self.maKhuVuc = maKhuVuc
        self.trangThai = trangThai

    def to_dict(self):
        return {
            "mavitri": self.maViTri,
            "makhuvuc": self.maKhuVuc,
            "trangthai": self.trangThai
        }
