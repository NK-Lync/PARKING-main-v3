class LuotGuiXe:
    def __init__(
        self,
        maLuotGui=None,
        bienSo=None,
        maLoaiXe=None,
        maViTri=None,
        loaiVe=None,
        thoiGianVao=None,
        thoiGianRa=None,
        tongPhi=None,
        tinhTrang=None
    ):
        self.maLuotGui = maLuotGui
        self.bienSo = bienSo
        self.maLoaiXe = maLoaiXe
        self.maViTri = maViTri
        self.loaiVe = loaiVe
        self.thoiGianVao = thoiGianVao
        self.thoiGianRa = thoiGianRa
        self.tongPhi = tongPhi
        self.tinhTrang = tinhTrang

    def to_dict(self):
        return {
            "maluotgui": self.maLuotGui,
            "bienso": self.bienSo,
            "maloaixe": self.maLoaiXe,
            "mavitri": self.maViTri,
            "loaive": self.loaiVe,
            "thoigianvao": self.thoiGianVao,
            "thoigianra": self.thoiGianRa,
            "tongphi": self.tongPhi,
            "tinhtrang": self.tinhTrang
        }
