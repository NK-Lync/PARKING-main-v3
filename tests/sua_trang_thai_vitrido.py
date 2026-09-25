# -*- coding: utf-8 -*-
"""
Sua hau qua: script test truoc do chup trang thai vitrido SAU khi xe da vao,
nen tra nham 3 vi tri ve 'Dang su dung' trong khi khong con xe nao do.

Trang thai dung (in ra o dong BASELINE cua ca 2 script truoc): ca 6 vi tri
'Con trong', va luotguixe chi con 2 dong cu (id 1, 2) deu 'Da tra'.

Script nay tra 6 vi tri ve 'Con trong' va kiem chung lai.
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# --- Cho phép chạy file này từ bất kỳ thư mục nào -----------------------
import os as _os
import sys as _sys

GOC_DU_AN = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if GOC_DU_AN not in _sys.path:
    _sys.path.insert(0, GOC_DU_AN)

DUONG_DAN_APP = _os.path.join(GOC_DU_AN, "app.py")
# -----------------------------------------------------------------------

from database.supabase_client import supabase

TRANG_THAI_DUNG = "Còn trống"

print("=== TRUOC KHI SUA ===")
truoc = supabase.table("vitrido").select("mavitri,trangthai").order("mavitri").execute().data
print(f"  vitrido: {[(v['mavitri'], v['trangthai']) for v in truoc]}")

luot = (
    supabase.table("luotguixe").select("maluotgui,bienso,tinhtrang")
    .eq("tinhtrang", "Đang gửi").execute().data
)
print(f"  luotguixe dang gui: {luot}")

# --- Sua: tra tung vi tri ve 'Con trong' ---
print("\n=== SUA ===")
for v in truoc:
    if v["trangthai"] != TRANG_THAI_DUNG:
        r = (
            supabase.table("vitrido")
            .update({"trangthai": TRANG_THAI_DUNG})
            .eq("mavitri", v["mavitri"])
            .execute()
        )
        print(f"  mavitri {v['mavitri']}: {v['trangthai']!r} -> {TRANG_THAI_DUNG!r}  "
              f"({len(r.data or [])} dong cap nhat)")
    else:
        print(f"  mavitri {v['mavitri']}: da dung, khong doi")

# --- Kiem chung ---
print("\n=== SAU KHI SUA ===")
sau = supabase.table("vitrido").select("mavitri,trangthai").order("mavitri").execute().data
print(f"  vitrido: {[(v['mavitri'], v['trangthai']) for v in sau]}")

con_sai = [v for v in sau if v["trangthai"] != TRANG_THAI_DUNG]
if con_sai:
    print(f"  !! CON SAI: {con_sai}")
else:
    print("  Ca 6 vi tri deu 'Con trong' - dung voi trang thai goc")

for ten in ["loaixe", "khuvuc", "vitrido", "luotguixe", "vethang", "taikhoan"]:
    r = supabase.table(ten).select("*", count="exact").execute()
    print(f"    {ten:12s} {r.count} dong")
