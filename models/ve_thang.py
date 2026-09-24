class VeThang:
    def __init__(
        self,
        maVe=None,
        bienSo=None,
        tenKhachHang=None,
        maLoaiXe=None,
        ngayDangKy=None,
        ngayHetHan=None,
        trangThai=None
    ):
        self.maVe = maVe
        self.bienSo = bienSo
        self.tenKhachHang = tenKhachHang
        self.maLoaiXe = maLoaiXe
        self.ngayDangKy = ngayDangKy
        self.ngayHetHan = ngayHetHan
        self.trangThai = trangThai

    def to_dict(self):
        return {
            "mave": self.maVe,
            "bienso": self.bienSo,
            "tenkhachhang": self.tenKhachHang,
            "maloaixe": self.maLoaiXe,
            "ngaydangky": self.ngayDangKy,
            "ngayhethan": self.ngayHetHan,
            "trangthai": self.trangThai
        }
