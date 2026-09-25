# -*- coding: utf-8 -*-
"""
Vong test qua HTTP THAT - kiem tang routes/ ma 2 vong truoc chua cham toi.

Script tu bat app.py, cho cong san sang, goi API bang urllib, roi tat server
va don sach.

DON SACH: chup trang thai vitrido TRUOC khi lam bat cu dieu gi (bai hoc tu
vong truoc), va chi xoa dung nhung maluotgui do chinh script nay tao ra.
"""

import sys
import io
import json
import time
import subprocess
import urllib.request
import urllib.error

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

BASE = "http://127.0.0.1:5000"
PLATE = "HTTPTEST-01"

TAO_RA = []
VITRI_GOC = {}

ok_count = 0
fail_count = 0
server = None


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


def goi(method, duong_dan, body=None):
    """Goi API, tra ve (status_code, dict)."""
    url = BASE + duong_dan
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def don_sach():
    line("DON SACH")
    if TAO_RA:
        print(f"  Xoa dung {len(TAO_RA)} dong luotguixe theo id: {sorted(TAO_RA)}")
        for mid in sorted(TAO_RA):
            x = supabase.table("luotguixe").delete().eq("maluotgui", mid).execute()
            print(f"    maluotgui={mid}: xoa {len(x.data or [])} dong")
    else:
        print("  Khong co dong nao do test tao ra.")

    if VITRI_GOC:
        print(f"  Tra {len(VITRI_GOC)} vi tri ve trang thai goc: {VITRI_GOC}")
        for mv, tt in VITRI_GOC.items():
            supabase.table("vitrido").update({"trangthai": tt}).eq("mavitri", mv).execute()


try:
    # ==========================================================
    line("BASELINE - CHUP TRUOC KHI LAM BAT CU DIEU GI")
    # ==========================================================
    vit = supabase.table("vitrido").select("mavitri,trangthai").order("mavitri").execute().data
    for v in vit:
        VITRI_GOC[v["mavitri"]] = v["trangthai"]
    print(f"  vitrido: {[(v['mavitri'], v['trangthai']) for v in vit]}")
    print("  (da luu lam trang thai goc de tra lai)")

    # ==========================================================
    line("BAT SERVER")
    # ==========================================================
    server = subprocess.Popen(
        [_sys.executable, DUONG_DAN_APP],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=GOC_DU_AN,
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )

    san_sang = False
    for _ in range(60):
        time.sleep(0.5)
        if server.poll() is not None:
            print("  Server thoat som! Log:")
            print(server.stdout.read().decode("utf-8", "replace")[:2000])
            break
        try:
            urllib.request.urlopen(BASE + "/api/parking/status", timeout=2)
            san_sang = True
            break
        except urllib.error.HTTPError:
            san_sang = True
            break
        except Exception:
            continue

    check("Server khoi dong va nhan ket noi", san_sang)
    if not san_sang:
        raise SystemExit("Khong bat duoc server")

    # ==========================================================
    line("1. TRANG CHU - SPA duoc phuc vu?")
    # ==========================================================
    try:
        with urllib.request.urlopen(BASE + "/", timeout=10) as r:
            html = r.read().decode("utf-8", "replace")
        check("GET / tra ve HTML", r.status == 200 and "<" in html,
              f"status={r.status}, {len(html)} ky tu")
    except Exception as e:
        check("GET / tra ve HTML", False, str(e)[:120])

    # ==========================================================
    line("2. DANG NHAP")
    # ==========================================================
    st, r = goi("POST", "/api/taikhoan/dang-nhap",
                {"tendangnhap": "admin", "matkhau": "admin123"})
    check("Dang nhap admin/admin123 thanh cong", st == 200 and r.get("success"),
          f"status={st}  {str(r)[:120]}")

    st, r = goi("POST", "/api/taikhoan/dang-nhap",
                {"tendangnhap": "admin", "matkhau": "sai-mat-khau"})
    check("Sai mat khau bi tu choi", st != 200 or not r.get("success"),
          f"status={st}  {r.get('message') if isinstance(r, dict) else r}")

    # ==========================================================
    line("3. TRANG THAI BAI XE")
    # ==========================================================
    st, r = goi("GET", "/api/parking/status")
    check("GET /api/parking/status tra 200", st == 200 and r.get("success"),
          f"status={st}")
    d = r["data"]
    check("Tra du 5 truong trang thai",
          all(k in d for k in ["tong_vi_tri", "dang_su_dung", "con_trong",
                               "ty_le_lap_day", "xe_dang_gui"]),
          f"{d['tong_vi_tri']} vi tri / {d['dang_su_dung']} dang dung / "
          f"{d['con_trong']} trong / {d['ty_le_lap_day']}%")

    # ==========================================================
    line("4. XE VAO - XE RA QUA HTTP")
    # ==========================================================
    st, r = goi("POST", "/api/parking/entry", {"bienso": PLATE, "maloaixe": 1})
    check("POST /api/parking/entry tra 201", st == 201 and r.get("success"),
          f"status={st}  {r.get('message')}")
    if r.get("success"):
        TAO_RA.append(r["data"]["luotgui"]["maluotgui"])
        print(f"         maluotgui={r['data']['luotgui']['maluotgui']}  "
              f"vi tri={r['data']['vitri']['mavitri']}  "
              f"khu={r['data']['vitri'].get('tenkhuvuc')!r}")

    st, r = goi("POST", "/api/parking/entry", {"bienso": PLATE, "maloaixe": 1})
    check("Vao bai lan 2 bi chan", st == 400,
          f"status={st}  {r.get('message') if isinstance(r, dict) else r}")

    st, r = goi("POST", "/api/parking/entry", {"maloaixe": 1})
    check("Thieu bien so -> 400", st == 400,
          f"status={st}  {r.get('message') if isinstance(r, dict) else r}")

    st, r = goi("POST", "/api/parking/exit", {"bienso": "KHONG-CO-XE-NAY"})
    check("Cho xe khong ton tai ra -> 400", st == 400,
          f"status={st}  {r.get('message') if isinstance(r, dict) else r}")

    st, r = goi("POST", "/api/parking/exit", {"bienso": PLATE})
    check("POST /api/parking/exit tra 200", st == 200 and r.get("success"),
          f"status={st}")
    if r.get("success"):
        d = r["data"]
        check("Tra ve day du thong tin tinh phi",
              all(k in d for k in ["tongphi", "so_gio_tinh_phi", "co_ve_thang",
                                   "thoigianvao", "thoigianra"]),
              f"phi={d['tongphi']}  {d['so_gio_tinh_phi']} gio  "
              f"ve thang={d['co_ve_thang']}")

    # ==========================================================
    line("5. CAC API DANH MUC")
    # ==========================================================
    for duong_dan, nhan in [
        ("/api/khuvuc", "khu vuc"),
        ("/api/vitrido", "vi tri do"),
        ("/api/loaixe", "loai xe"),
        ("/api/luotguixe", "luot gui xe"),
        ("/api/vethang", "ve thang"),
        ("/api/taikhoan", "tai khoan"),
        ("/api/khuvuc/cho-trong", "cho trong theo khu vuc"),
    ]:
        st, r = goi("GET", duong_dan)
        so = len(r.get("data", [])) if isinstance(r, dict) and isinstance(r.get("data"), list) else "-"
        check(f"GET {duong_dan} ({nhan})", st == 200, f"status={st}  {so} ban ghi")

    # ==========================================================
    line("6. THONG KE")
    # ==========================================================
    for duong_dan in ["/api/thongke/luu-luong", "/api/thongke/doanh-thu",
                      "/api/thongke/phan-tich"]:
        st, r = goi("GET", duong_dan)
        check(f"GET {duong_dan}", st == 200, f"status={st}")

    # ==========================================================
    line("7. XOA VI TRI BAT BUOC - /api/khuvuc/cap-nhat")
    # ==========================================================
    st, r = goi("POST", "/api/khuvuc/cap-nhat")
    check("POST /api/khuvuc/cap-nhat chay duoc", st == 200,
          f"status={st}  {str(r)[:140]}")

    # ==========================================================
    line("8. /api/ai/* - endpoint GenAI (khong can anh)")
    # ==========================================================
    st, r = goi("POST", "/api/ai/bao-cao-luu-luong")
    if isinstance(r, dict):
        nguon = r.get("data", {}).get("nguon") if isinstance(r.get("data"), dict) else None
        check(f"POST /api/ai/bao-cao-luu-luong (status={st})", st == 200,
              f"nguon={nguon!r}  {str(r.get('message'))[:100]}")
        if nguon == "noi-bo" and r.get("data", {}).get("canh_bao"):
            print(f"         canh bao: {r['data']['canh_bao'][:140]}")
    else:
        check("POST /api/ai/bao-cao-luu-luong", False, str(r)[:140])

finally:
    if server and server.poll() is None:
        print("\n  Dang tat server...")
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)
        print(f"  Server da tat (ma thoat {server.returncode}).")

    try:
        don_sach()
    except Exception as e:
        print(f"  !! DON SACH LOI: {e}")

    line("KET QUA")
    print(f"  DAT : {ok_count}")
    print(f"  HONG: {fail_count}")

    vit = supabase.table("vitrido").select("mavitri,trangthai").order("mavitri").execute().data
    print(f"\n  vitrido: {[(v['mavitri'], v['trangthai']) for v in vit]}")
    khop = all(v["trangthai"] == VITRI_GOC.get(v["mavitri"]) for v in vit)
    print(f"  Khop trang thai goc: {'CO' if khop else 'KHONG - CAN KIEM TRA'}")

    luot = supabase.table("luotguixe").select("maluotgui,bienso,tinhtrang").order("maluotgui").execute().data
    print(f"  luotguixe: {[(l['maluotgui'], l['bienso'], l['tinhtrang']) for l in luot]}")
    for ten in ["loaixe", "khuvuc", "vitrido", "luotguixe", "vethang", "taikhoan"]:
        r = supabase.table(ten).select("*", count="exact").execute()
        print(f"    {ten:12s} {r.count} dong")
