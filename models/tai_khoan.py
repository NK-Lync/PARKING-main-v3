class TaiKhoan:
    def __init__(
        self,
        maND=None,
        tenDangNhap=None,
        matKhau=None,
        vaiTro=None,
        trangThai=None,
        email=None,
        soDienThoai=None
    ):
        self.maND = maND
        self.tenDangNhap = tenDangNhap
        self.matKhau = matKhau
        self.vaiTro = vaiTro
        self.trangThai = trangThai
        self.email = email
        self.soDienThoai = soDienThoai

    def to_dict(self):
        return {
            "mand": self.maND,
            "tendangnhap": self.tenDangNhap,
            "matkhau": self.matKhau,
            "vaitro": self.vaiTro,
            "trangthai": self.trangThai,
            "email": self.email,
            "sodienthoai": self.soDienThoai
        }
