# -*- coding: utf-8 -*-
"""
Vong test thu 2 - chay lai 4 diem da "hong" o vong 1, lan nay viet dung gia thiet.

Vong 1 that bai 4 muc, nhung 3 muc la do test viet sai:
  - Gia dinh "lan 2 phai chon cho khac lan 1" -> SAI, vi cho 1 da duoc tra
    tu do sau khi xe 1 ra, nen chon lai cho 1 la DUNG.
  - Vi the phep thu index bien so bi lech: no vi pham index VI TRI truoc.
  - Tuong tu, "vi tri 2 van con trong" sai vi vi tri 2 chinh la vi tri 1.

Vong nay kiem cho that:
  A. unique_active_parking_plate  (chua he duoc kiem)
  B. Nhanh `overridden` cua sync_ai_occupancy (chua he duoc kiem)
  C. Quy tac chon cho: luon lay vi tri co so nho nhat con trong

DON SACH: chi xoa dung nhung maluotgui ma script nay tao ra (theo doi trong
TAO_RA), va chi tra nhung mavitri ma script nay dung toi (theo doi trong
VITRI_CHAM). Khong dung bo loc tinh toan luc chay.
"""

import sys
import io
import traceback

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
from services.parking_service import ParkingService

# --- So sach: id cu the do test tao ra, va vi tri cu the bi cham toi ---
TAO_RA = []        # danh sach maluotgui
VITRI_CHAM = {}    # {mavitri: trangthai_goc}

PA = "TESTPLATE-A"
PB = "TESTPLATE-B"
PC = ["TESTPLATE-C1", "TESTPLATE-C2", "TESTPLATE-C3", "TESTPLATE-C4"]

ok_count = 0
fail_count = 0


def line(t=""):
    print("\n" + "=" * 64)
    if t:
        print(t)
        print("=" * 64)


def check(label, dk, ct=""):
    global ok_count, fail_count
    if dk:
        ok_count += 1
        print(f"  [DAT]  {label}")
    else:
        fail_count += 1
        print(f"  [HONG] {label}")
    if ct:
        print(f"         {ct}")


def ghi_nho(maluotgui):
    TAO_RA.append(maluotgui)
    return maluotgui


def nho_vi_tri(mavitri):
    """Ghi lai trang thai goc cua vi tri truoc khi dong vao lan dau."""
    if mavitri not in VITRI_CHAM:
        goc = (
            supabase.table("vitrido").select("trangthai")
            .eq("mavitri", mavitri).execute().data[0]["trangthai"]
        )
        VITRI_CHAM[mavitri] = goc
    return mavitri


def vi_tri_cua(bien_so):
    r = (
        supabase.table("luotguixe").select("maluotgui,mavitri")
        .eq("bienso", bien_so).eq("tinhtrang", "Đang gửi").execute().data
    )
    return r[0] if r else None


def trang_thai_vitri(mavitri):
    return (
        supabase.table("vitrido").select("trangthai").eq("mavitri", mavitri)
        .execute().data[0]["trangthai"]
    )


def vao_bai(bien_so, ma_loai, vi_tri=None):
    """Vao bai + ghi nho maluotgui va mavitri de don sach."""
    if vi_tri is None:
        kq = ParkingService.vehicle_entry(bien_so, ma_loai)
    else:
        kq = ParkingService.vehicle_entry_at_position(bien_so, ma_loai, vi_tri)
    if kq.get("success"):
        ghi_nho(kq["data"]["luotgui"]["maluotgui"])
        nho_vi_tri(kq["data"]["vitri"]["mavitri"])
    return kq


def don_sach():
    line("DON SACH")
    if not TAO_RA:
        print("  Khong co dong nao do test tao ra - khong xoa gi.")
    else:
        print(f"  Se xoa dung {len(TAO_RA)} dong luotguixe theo id cu the: {sorted(TAO_RA)}")
        for mid in sorted(TAO_RA):
            x = supabase.table("luotguixe").delete().eq("maluotgui", mid).execute()
            print(f"    maluotgui={mid}: xoa {len(x.data or [])} dong")

    if not VITRI_CHAM:
        print("  Khong co vi tri nao bi cham - khong tra gi.")
    else:
        print(f"  Se tra {len(VITRI_CHAM)} vi tri ve trang thai goc: {VITRI_CHAM}")
        for mv, tt in VITRI_CHAM.items():
            supabase.table("vitrido").update({"trangthai": tt}).eq("mavitri", mv).execute()


try:
    line("BASELINE")
    vit = supabase.table("vitrido").select("*").order("mavitri").execute().data
    luot = supabase.table("luotguixe").select("maluotgui").execute().data
    print(f"  vitrido  : {[(v['mavitri'], v['trangthai']) for v in vit]}")
    print(f"  luotguixe: {len(luot)} dong, id = {sorted(l['maluotgui'] for l in luot)}")

    ma_loai = supabase.table("loaixe").select("*").eq("maloaixe", 1).execute().data[0]["maloaixe"]

    # ==========================================================
    line("A. INDEX unique_active_parking_plate (chua tung duoc kiem)")
    # ==========================================================
    vao = vao_bai(PA, ma_loai)
    check("Xe A vao bai", vao["success"], vao["message"])
    vitri_A = vao["data"]["vitri"]["mavitri"]

    vitri_khac = next(
        v["mavitri"] for v in vit
        if v["mavitri"] != vitri_A and v["trangthai"] == "Còn trống"
    )
    check("Vi tri dich khac vi tri xe A dang do", vitri_khac != vitri_A,
          f"xe A o cho {vitri_A}, se thu chen trung bien so vao cho {vitri_khac}")

    try:
        supabase.table("luotguixe").insert({
            "bienso": PA, "maloaixe": ma_loai, "mavitri": vitri_khac,
            "thoigianvao": "2026-09-25T00:00:00", "tongphi": 0,
            "tinhtrang": "Đang gửi",
        }).execute()
        check("Index unique_active_parking_plate chan trung bien so", False,
              "KHONG bi chan -> index KHONG ton tai!")
    except Exception as e:
        msg = str(e)
        check("Index unique_active_parking_plate chan dung",
              "unique_active_parking_plate" in msg, f"loi: {msg[:150]}")

    check("Vi tri dich khong bi ban sau khi chen loi",
          trang_thai_vitri(vitri_khac) == "Còn trống",
          f"trangthai cho {vitri_khac} = {trang_thai_vitri(vitri_khac)!r}")

    ParkingService.vehicle_exit(PA)

    # ==========================================================
    line("B. Nhanh `overridden` - sua vi tri bi lech trang thai")
    # ==========================================================
    vao = vao_bai(PB, ma_loai)
    check("Xe B vao bai", vao["success"], vao["message"])
    vitri_B = vao["data"]["vitri"]["mavitri"]
    print(f"  Xe B dang o cho {vitri_B}")

    # Co tinh lam lech: xe dang do ma vi tri lai ghi "Con trong"
    supabase.table("vitrido").update({"trangthai": "Còn trống"}).eq(
        "mavitri", vitri_B
    ).execute()
    check("Da co tinh lam lech trang thai vi tri",
          trang_thai_vitri(vitri_B) == "Còn trống",
          f"cho {vitri_B} ghi {trang_thai_vitri(vitri_B)!r} nhung xe VAN dang do that")

    kq = ParkingService.sync_ai_occupancy({
        "success": True,
        "data": {"vi_tri": [{"mavitri": vitri_B, "trangthai": "Còn trống"}]},
    })
    ad = kq["data"]
    check("AI bi chan va vi tri duoc SUA LAI",
          ad["so_vi_tri_bao_ve_nghiep_vu"] == 1 and ad["so_vi_tri_cap_nhat"] == 0,
          f"cap nhat={ad['so_vi_tri_cap_nhat']} bao ve={ad['so_vi_tri_bao_ve_nghiep_vu']} "
          f"khong doi={ad['so_vi_tri_khong_doi']}")
    if ad["vi_tri_bi_ghi_de_boi_nghiep_vu"]:
        o = ad["vi_tri_bi_ghi_de_boi_nghiep_vu"][0]
        print(f"         {o['trangthai_cu']!r} -> {o['trangthai_cuoi']!r}  ({o['reason']})")

    check("Vi tri da duoc sua ve 'Dang su dung'",
          trang_thai_vitri(vitri_B) == "Đang sử dụng",
          f"trangthai = {trang_thai_vitri(vitri_B)!r}")

    kq2 = ParkingService.sync_ai_occupancy({
        "success": True,
        "data": {"vi_tri": [{"mavitri": vitri_B, "trangthai": "Còn trống"}]},
    })
    ad2 = kq2["data"]
    check("Dong bo lan 2 (DB da dung) roi vao nhom 'khong doi'",
          ad2["so_vi_tri_khong_doi"] == 1 and ad2["so_vi_tri_cap_nhat"] == 0,
          f"cap nhat={ad2['so_vi_tri_cap_nhat']} bao ve={ad2['so_vi_tri_bao_ve_nghiep_vu']} "
          f"khong doi={ad2['so_vi_tri_khong_doi']}")

    ParkingService.vehicle_exit(PB)

    # ==========================================================
    line("C. Quy tac chon cho: luon lay vi tri so nho nhat con trong")
    # ==========================================================
    tt = ParkingService.get_status()["data"]
    check("Bai trong hoan toan truoc khi kiem", tt["dang_su_dung"] == 0,
          f"{tt['con_trong']} cho trong")

    v1 = vao_bai(PC[0], ma_loai)
    v2 = vao_bai(PC[1], ma_loai)
    v3 = vao_bai(PC[2], ma_loai)
    day = [v1["data"]["vitri"]["mavitri"], v2["data"]["vitri"]["mavitri"],
           v3["data"]["vitri"]["mavitri"]]
    check("3 xe dau chiem dung cho 1, 2, 3", day == [1, 2, 3], f"nhan duoc {day}")

    ParkingService.vehicle_exit(PC[1])
    v4 = vao_bai(PC[3], ma_loai)
    check("Cho trong o giua duoc lap lai truoc (cho 2, khong phai cho 4)",
          v4["data"]["vitri"]["mavitri"] == 2,
          f"xe 4 vao cho {v4['data']['vitri']['mavitri']}")

    tt = ParkingService.get_status()["data"]
    check("Bao dung 3 cho dang dung", tt["dang_su_dung"] == 3,
          f"{tt['dang_su_dung']} dang dung / {tt['con_trong']} trong / "
          f"ty le {tt['ty_le_lap_day']}%")

    for p in [PC[0], PC[2], PC[3]]:
        ParkingService.vehicle_exit(p)

    tt = ParkingService.get_status()["data"]
    check("Tra het xe -> bai trong lai", tt["dang_su_dung"] == 0,
          f"{tt['dang_su_dung']} dang dung / {tt['con_trong']} trong")

finally:
    try:
        don_sach()
    except Exception:
        print("  !! DON SACH THAT BAI !!")
        traceback.print_exc()

    line("KET QUA")
    print(f"  DAT : {ok_count}")
    print(f"  HONG: {fail_count}")

    vit = supabase.table("vitrido").select("mavitri,trangthai").order("mavitri").execute().data
    luot = (
        supabase.table("luotguixe").select("maluotgui,bienso,tinhtrang")
        .order("maluotgui").execute().data
    )
    print(f"\n  vitrido  : {[(v['mavitri'], v['trangthai']) for v in vit]}")
    print(f"  luotguixe: {[(l['maluotgui'], l['bienso'], l['tinhtrang']) for l in luot]}")
    for ten in ["loaixe", "khuvuc", "vitrido", "luotguixe", "vethang", "taikhoan"]:
        r = supabase.table(ten).select("*", count="exact").execute()
        print(f"    {ten:12s} {r.count} dong")
