class KhuVuc:
    def __init__(
        self,
        maKhuVuc=None,
        tenKhuVuc=None,
        tongSoViTri=None,
        soXeHienTai=None
    ):
        self.maKhuVuc = maKhuVuc
        self.tenKhuVuc = tenKhuVuc
        self.tongSoViTri = tongSoViTri
        self.soXeHienTai = soXeHienTai

    def to_dict(self):
        return {
            "makhuvuc": self.maKhuVuc,
            "tenkhuvuc": self.tenKhuVuc,
            "tongsovitri": self.tongSoViTri,
            "soxehientai": self.soXeHienTai
        }
