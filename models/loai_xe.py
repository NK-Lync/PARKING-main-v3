class LoaiXe:
    def __init__(self, maLoaiXe=None, tenLoaiXe=None, donGia=None):
        self.maLoaiXe = maLoaiXe
        self.tenLoaiXe = tenLoaiXe
        self.donGia = donGia

    def to_dict(self):
        return {
            "maloaixe": self.maLoaiXe,
            "tenloaixe": self.tenLoaiXe,
            "dongia": self.donGia
        }