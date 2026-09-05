class VeThang:
    def __init__(
        self,
        maVe=None,
        bienSo=None,
        ngayHetHan=None,
        trangThai=None
    ):
        self.maVe = maVe
        self.bienSo = bienSo
        self.ngayHetHan = ngayHetHan
        self.trangThai = trangThai

    def to_dict(self):
        return {
            "mave": self.maVe,
            "bienso": self.bienSo,
            "ngayhethan": self.ngayHetHan,
            "trangthai": self.trangThai
        }