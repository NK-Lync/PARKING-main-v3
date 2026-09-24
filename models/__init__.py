"""Tầng mô hình (Model) - phản ánh các lớp trong mô hình lớp OOD.

Các lớp ở đây tương ứng 1-1 với các bảng trong cơ sở dữ liệu
Supabase/PostgreSQL (xem database/schema.sql).
"""
from .loai_xe import LoaiXe
from .khu_vuc import KhuVuc
from .vi_tri_do import ViTriDo
from .luot_gui_xe import LuotGuiXe
from .ve_thang import VeThang
from .tai_khoan import TaiKhoan

__all__ = [
    "LoaiXe",
    "KhuVuc",
    "ViTriDo",
    "LuotGuiXe",
    "VeThang",
    "TaiKhoan",
]
