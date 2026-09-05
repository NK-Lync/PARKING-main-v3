class ViTriDo:
    def __init__(
        self,
        maViTri=None,
        tenKhuVuc=None,
        trangThai=None
    ):
        self.maViTri = maViTri
        self.tenKhuVuc = tenKhuVuc
        self.trangThai = trangThai

    def to_dict(self):
        return {
            "mavitri": self.maViTri,
            "tenkhuvuc": self.tenKhuVuc,
            "trangthai": self.trangThai
        }