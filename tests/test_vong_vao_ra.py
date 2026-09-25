# -*- coding: utf-8 -*-
"""
Chay thu vong vao -> ra that tren Supabase, roi DON SACH.

Muc dich:
  1. Xac nhan nghiep vu xe vao / xe ra chay dung tren DB that.
  2. Xac nhan 2 partial unique index (unique_active_parking_position,
     unique_active_parking_plate) CO THAT va dang chan dung.
  3. Xac nhan tang bao ve nghiep vu: AI noi "Con trong" nhung co xe
     active thi KHONG duoc giai phong vi tri.
  4. Xac nhan duong ve thang (mien phi).

Nguyen tac: baseline truoc, finally don sach.
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

LOAI_RA = []
VITRI_GOC = {}
MAX_LUOT_GOC = 0

PLATE_1 = "TEST0001"
PLATE_2 = "TEST0002"
PLATE_3 = "TEST0003"
PLATE_4 = "TEST0004"
PLATE_5 = "TEST0005"

ok_count = 0
fail_count = 0


def line(title=""):
    print("\n" + "=" * 64)
    if title:
        print(title)
        print("=" * 64)


def check(label, dieu_kien, chi_tiet=""):
    global ok_count, fail_count
    if dieu_kien:
        ok_count += 1
        print(f"  [DAT]  {label}")
    else:
        fail_count += 1
        print(f"  [HONG] {label}")
    if chi_tiet:
        print(f"         {chi_tiet}")


def snapshot():
    """Chup lai trang thai goc de khoi phuc."""
    vit = (
        supabase.table("vitrido")
        .select("mavitri,makhuvuc,trangthai")
        .order("mavitri")
        .execute()
        .data
    )
    luot = (
        supabase.table("luotguixe")
        .select("maluotgui,bienso,tinhtrang")
        .order("maluotgui")
        .execute()
        .data
    )
    return vit, luot


def dem_bang():
    """Dem so dong tung bang - de chung minh khong con rac sau khi don."""
    ket_qua = {}
    for ten in ["loaixe", "khuvuc", "vitrido", "luotguixe", "vethang", "taikhoan"]:
        r = supabase.table(ten).select("*", count="exact").execute()
        ket_qua[ten] = r.count
    return ket_qua


def khoi_phuc():
    """Xoa moi luot gui tao ra trong luc test + tra trang thai vitrido ve goc."""
    line("DON SACH")

    xoa = (
        supabase.table("luotguixe")
        .delete()
        .gt("maluotgui", MAX_LUOT_GOC)
        .execute()
    )
    print(f"  Da xoa {len(xoa.data or [])} luot gui tao trong luc test "
          f"(maluotgui > {MAX_LUOT_GOC})")

    for mavitri, trangthai_goc in VITRI_GOC.items():
        (
            supabase.table("vitrido")
            .update({"trangthai": trangthai_goc})
            .eq("mavitri", mavitri)
            .execute()
        )
    print(f"  Da tra {len(VITRI_GOC)} vi tri ve trang thai goc: {VITRI_GOC}")

    con_lai, luot_con = snapshot()
    print(f"  vitrido  : {[(v['mavitri'], v['trangthai']) for v in con_lai]}")
    print(f"  luotguixe: {[(l['maluotgui'], l['bienso'], l['tinhtrang']) for l in luot_con]}")


try:
    # ==========================================================
    line("BUOC 0 - CHUP TRANG THAI GOC (BASELINE)")
    # ==========================================================
    vit_goc, luot_goc = snapshot()

    for v in vit_goc:
        VITRI_GOC[v["mavitri"]] = v["trangthai"]

    MAX_LUOT_GOC = max((l["maluotgui"] for l in luot_goc), default=0)

    print(f"  vitrido  : {[(v['mavitri'], v['makhuvuc'], v['trangthai']) for v in vit_goc]}")
    print(f"  luotguixe: {[(l['maluotgui'], l['bienso'], l['tinhtrang']) for l in luot_goc]}")
    print(f"  maluotgui lon nhat hien co = {MAX_LUOT_GOC}  (moi dong > muc nay la rac cua test)")

    loai_xe = supabase.table("loaixe").select("*").order("maloaixe").execute().data
    print(f"  loaixe   : {[(x['maloaixe'], x['tenloaixe'], x['dongia']) for x in loai_xe]}")

    ve_thang = supabase.table("vethang").select("*").execute().data
    print(f"  vethang  : {[(x['mave'], x['bienso'], x['ngayhethan'], x['trangthai']) for x in ve_thang]}")

    trang_thai = ParkingService.get_status()["data"]
    print(f"  get_status luc dau: {trang_thai['tong_vi_tri']} vi tri / "
          f"{trang_thai['dang_su_dung']} dang dung / {trang_thai['con_trong']} trong")

    ma_loai_1 = loai_xe[0]["maloaixe"]
    ma_loai_2 = loai_xe[1]["maloaixe"]
    gia_1 = loai_xe[0]["dongia"]
    gia_2 = loai_xe[1]["dongia"]

    # ==========================================================
    line("VONG 1 - XE VAO TU DONG CHON CHO, ROI RA")
    # ==========================================================
    vao = ParkingService.vehicle_entry(PLATE_1, ma_loai_1)
    check("Xe vao bai thanh cong", vao["success"], vao["message"])

    luot_1 = vao["data"]["luotgui"]
    vitri_1 = vao["data"]["vitri"]["mavitri"]
    print(f"         maluotgui={luot_1['maluotgui']}  mavitri={vitri_1}  "
          f"khu={vao['data']['vitri'].get('tenkhuvuc')}  tinhtrang={luot_1['tinhtrang']}")

    check("Khu vuc hien ra ten (khong phai None)",
          vao["data"]["vitri"].get("tenkhuvuc") is not None,
          f"tenkhuvuc = {vao['data']['vitri'].get('tenkhuvuc')!r}")

    tt = ParkingService.get_status()["data"]
    check("get_status bao dung 1 cho dang dung", tt["dang_su_dung"] == 1,
          f"{tt['dang_su_dung']} dang dung / {tt['con_trong']} trong / "
          f"ty le {tt['ty_le_lap_day']}%")
    check("Danh sach xe dang gui co dung bien so",
          any(x["bienso"] == PLATE_1 for x in tt["xe_dang_gui"]))

    vi_tri_db = (
        supabase.table("vitrido").select("*").eq("mavitri", vitri_1).execute().data[0]
    )
    check("Vi tri duoc danh dau 'Dang su dung'",
          vi_tri_db["trangthai"] == "Đang sử dụng", f"trangthai = {vi_tri_db['trangthai']!r}")

    ra = ParkingService.vehicle_exit(PLATE_1)
    check("Xe ra khoi bai thanh cong", ra["success"], ra["message"])
    d = ra["data"]
    check("Tinh phi dung (1 gio x don gia)",
          d["tongphi"] == gia_1,
          f"{d['so_gio_tinh_phi']} gio x {gia_1} = {d['tongphi']}  "
          f"(gui {d['thoigian_gui_phut']} phut, ve thang = {d['co_ve_thang']})")

    vi_tri_db = (
        supabase.table("vitrido").select("*").eq("mavitri", vitri_1).execute().data[0]
    )
    check("Vi tri duoc tra ve 'Con trong'",
          vi_tri_db["trangthai"] == "Còn trống", f"trangthai = {vi_tri_db['trangthai']!r}")

    # ==========================================================
    line("VONG 2 - XE THU HAI, KHAC LOAI XE")
    # ==========================================================
    vao2 = ParkingService.vehicle_entry(PLATE_2, ma_loai_2)
    check("Xe thu hai vao bai thanh cong", vao2["success"], vao2["message"])

    luot_2 = vao2["data"]["luotgui"]
    vitri_2 = vao2["data"]["vitri"]["mavitri"]
    print(f"         maluotgui={luot_2['maluotgui']}  mavitri={vitri_2}")

    check("Chon vi tri KHAC lan truoc", vitri_2 != vitri_1,
          f"lan 1 = mavitri {vitri_1}, lan 2 = mavitri {vitri_2}")

    # Xe dang trong bai thi khong duoc vao lai
    vao_lai = ParkingService.vehicle_entry(PLATE_2, ma_loai_2)
    check("Chan xe da o trong bai vao lai",
          not vao_lai["success"] and "đang ở trong bãi" in vao_lai["message"],
          vao_lai["message"])

    ra2 = ParkingService.vehicle_exit(PLATE_2)
    check("Xe thu hai ra thanh cong", ra2["success"], ra2["message"])
    check("Tinh phi theo don gia loai xe 2",
          ra2["data"]["tongphi"] == gia_2,
          f"{ra2['data']['so_gio_tinh_phi']} gio x {gia_2} = {ra2['data']['tongphi']}")

    # ==========================================================
    line("VONG 3 - XE VAO ROI RA LAN NUA (kiem tra tai lap)")
    # ==========================================================
    vao3 = ParkingService.vehicle_entry(PLATE_3, ma_loai_1)
    check("Xe thu ba vao bai thanh cong", vao3["success"], vao3["message"])
    vitri_3 = vao3["data"]["vitri"]["mavitri"]
    print(f"         maluotgui={vao3['data']['luotgui']['maluotgui']}  mavitri={vitri_3}")

    ra3 = ParkingService.vehicle_exit(PLATE_3)
    check("Xe thu ba ra thanh cong", ra3["success"], ra3["message"])

    tt = ParkingService.get_status()["data"]
    check("Bai xe sach tro lai sau 3 vong", tt["dang_su_dung"] == 0,
          f"{tt['dang_su_dung']} dang dung / {tt['con_trong']} trong")

    # ==========================================================
    line("VONG 4 - 2 PARTIAL UNIQUE INDEX CO THAT KHONG?")
    # Chen thang vao bang, KHONG qua service (service co tien-kiem-tra
    # nen se chan truoc khi cham toi index).
    # ==========================================================
    vao4 = ParkingService.vehicle_entry_at_position(PLATE_4, ma_loai_1, vitri_1)
    check("Xe vao dung vi tri chi dinh", vao4["success"], vao4["message"])

    print("\n  -- Chen thang 1 dong active thu hai vao CUNG vi tri --")
    try:
        supabase.table("luotguixe").insert({
            "bienso": PLATE_5,
            "maloaixe": ma_loai_1,
            "mavitri": vitri_1,
            "thoigianvao": "2026-09-25T00:00:00",
            "tongphi": 0,
            "tinhtrang": "Đang gửi",
        }).execute()
        check("Index unique_active_parking_position chan 2 xe cung 1 cho", False,
              "KHONG bi chan - index co the KHONG ton tai!")
    except Exception as e:
        ten = "unique_active_parking_position"
        check(f"Index {ten} chan dung", ten in str(e),
              f"loi tra ve: {str(e)[:160]}")

    print("\n  -- Chen thang 1 dong active thu hai voi CUNG bien so --")
    try:
        supabase.table("luotguixe").insert({
            "bienso": PLATE_4,
            "maloaixe": ma_loai_1,
            "mavitri": vitri_2,
            "thoigianvao": "2026-09-25T00:00:00",
            "tongphi": 0,
            "tinhtrang": "Đang gửi",
        }).execute()
        check("Index unique_active_parking_plate chan 2 luot active cung bien so",
              False, "KHONG bi chan - index co the KHONG ton tai!")
    except Exception as e:
        ten = "unique_active_parking_plate"
        check(f"Index {ten} chan dung", ten in str(e),
              f"loi tra ve: {str(e)[:160]}")

    print("\n  -- Vi tri khac van trong (2 lan chen loi khong tao dong rac) --")
    vitri_2_db = (
        supabase.table("vitrido").select("*").eq("mavitri", vitri_2).execute().data[0]
    )
    check("Vi tri 2 van 'Con trong'", vitri_2_db["trangthai"] == "Còn trống",
          f"trangthai = {vitri_2_db['trangthai']!r}")

    ParkingService.vehicle_exit(PLATE_4)

    # ==========================================================
    line("VONG 5 - AI KHONG DUOC GHI DE NGHIEP VU")
    # AI bao 'Con trong' trong khi van co xe active -> phai bi chan.
    # ==========================================================
    vao5 = ParkingService.vehicle_entry(PLATE_5, ma_loai_1)
    check("Xe vao de test tang bao ve", vao5["success"], vao5["message"])
    vitri_5 = vao5["data"]["vitri"]["mavitri"]
    print(f"         Xe {PLATE_5} dang o mavitri {vitri_5}")

    ket_qua_ai = ParkingService.sync_ai_occupancy({
        "success": True,
        "data": {"vi_tri": [{"mavitri": vitri_5, "trangthai": "Còn trống"}]},
    })
    ad = ket_qua_ai["data"]
    check("AI bi chan ghi de (khong giai phong cho co xe)",
          ad["so_vi_tri_bao_ve_nghiep_vu"] == 1 and ad["so_vi_tri_cap_nhat"] == 0,
          f"cap nhat={ad['so_vi_tri_cap_nhat']}  "
          f"bao ve={ad['so_vi_tri_bao_ve_nghiep_vu']}  "
          f"khong doi={ad['so_vi_tri_khong_doi']}")
    if ad["vi_tri_bi_ghi_de_boi_nghiep_vu"]:
        print(f"         ly do: {ad['vi_tri_bi_ghi_de_boi_nghiep_vu'][0]['reason']}")

    vitri_5_db = (
        supabase.table("vitrido").select("*").eq("mavitri", vitri_5).execute().data[0]
    )
    check("Vi tri van 'Dang su dung' sau khi AI bao trong",
          vitri_5_db["trangthai"] == "Đang sử dụng",
          f"trangthai = {vitri_5_db['trangthai']!r}")

    ParkingService.vehicle_exit(PLATE_5)

    # ==========================================================
    line("VONG 6 - VE THANG CO DUOC MIEN PHI KHONG?")
    # ==========================================================
    if ve_thang:
        bien_ve = ve_thang[0]["bienso"]
        print(f"  Dung bien so co ve thang: {bien_ve}")

        vao6 = ParkingService.vehicle_entry(bien_ve, ma_loai_1)
        if vao6["success"]:
            ra6 = ParkingService.vehicle_exit(bien_ve)
            d6 = ra6["data"]
            check("Xe co ve thang duoc mien phi", d6["tongphi"] == 0,
                  f"co_ve_thang={d6['co_ve_thang']}  tongphi={d6['tongphi']}")
        else:
            check("Xe co ve thang vao duoc bai", False, vao6["message"])
    else:
        print("  Khong co ve thang nao trong DB - bo qua vong nay")

    # ==========================================================
    line("KIEM TRA CUOI - DU LIEU NGHIEP VU CON NGUYEN?")
    # ==========================================================
    luot_cu = (
        supabase.table("luotguixe")
        .select("maluotgui,bienso,tinhtrang,tongphi")
        .lte("maluotgui", MAX_LUOT_GOC)
        .order("maluotgui")
        .execute()
        .data
    )
    truoc = [(l["maluotgui"], l["bienso"], l["tinhtrang"]) for l in luot_goc]
    sau = [(l["maluotgui"], l["bienso"], l["tinhtrang"]) for l in luot_cu]
    check("Cac luot gui CU khong bi dung toi", truoc == sau,
          f"truoc={truoc}  sau={sau}")

    vit_cu = (
        supabase.table("vitrido")
        .select("mavitri,makhuvuc,trangthai")
        .order("mavitri")
        .execute()
        .data
    )
    truoc_v = [(v["mavitri"], v["makhuvuc"], v["trangthai"]) for v in vit_goc]
    sau_v = [(v["mavitri"], v["makhuvuc"], v["trangthai"]) for v in vit_cu]
    check("Trang thai 6 vi tri giong het luc dau", truoc_v == sau_v,
          f"truoc={truoc_v}\n         sau  ={sau_v}")

finally:
    line("DON SACH")
    try:
        khoi_phuc()
    except Exception:
        print("  !! DON SACH THAT BAI - CAN XU LY TAY !!")
        traceback.print_exc()

    line("KET QUA")
    print(f"  DAT : {ok_count}")
    print(f"  HONG: {fail_count}")
    print("\n  So dong tung bang sau khi don:")
    try:
        for ten, so in dem_bang().items():
            print(f"    {ten:12s} {so}")
    except Exception as e:
        print(f"    khong dem duoc: {e}")
