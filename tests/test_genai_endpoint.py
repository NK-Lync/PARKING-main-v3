# -*- coding: utf-8 -*-
"""
Chay app voi AI_MODEL_NAME duoc ghi de, de chung minh: chi can doi ten model
trong .env la tang GenAI hoat dong that.

Khong sua file .env. Cac endpoint /api/ai/* chi doc du lieu, khong ghi.
"""

import sys
import io
import os
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


BASE = "http://127.0.0.1:5000"
# Lay tu moi truong de doi model chi bang mot bien, khong phai sua file:
#   AI_MODEL_NAME=<ten model> python tests/test_genai_endpoint.py
MODEL_MOI = os.environ.get("AI_MODEL_NAME") or "gemini-3.1-flash-lite"

ok_count = 0
fail_count = 0
server = None


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
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + duong_dan, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {}


try:
    print("=" * 64)
    print(f"BAT SERVER voi AI_MODEL_NAME={MODEL_MOI} (ghi de qua moi truong)")
    print("=" * 64)

    moi_truong = {**os.environ, "PYTHONIOENCODING": "utf-8",
                  "AI_MODEL_NAME": MODEL_MOI}

    server = subprocess.Popen(
        [_sys.executable, DUONG_DAN_APP],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=GOC_DU_AN, env=moi_truong,
    )

    san_sang = False
    for _ in range(60):
        time.sleep(0.5)
        if server.poll() is not None:
            print("  Server thoat som:")
            print(server.stdout.read().decode("utf-8", "replace")[:1500])
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

    check("Server khoi dong", san_sang)
    if not san_sang:
        raise SystemExit(1)

    print("\n" + "=" * 64)
    print("GOI 4 ENDPOINT /api/ai/*")
    print("=" * 64)

    for duong_dan, body in [
        ("/api/ai/bao-cao-luu-luong", None),
        ("/api/ai/gio-cao-diem", None),
        ("/api/ai/goi-y-nhan-su", None),
        ("/api/ai/hoi-dap", {"cau_hoi": "Bai xe hien co bao nhieu cho trong?"}),
    ]:
        st, r = goi("POST", duong_dan, body)
        d = r.get("data") if isinstance(r.get("data"), dict) else {}
        nguon = d.get("nguon")
        canh_bao = d.get("canh_bao")

        # Tim truong van ban tra loi, ten co the khac nhau tuy endpoint
        van_ban = ""
        for k in ["tra_loi", "bao_cao", "phan_tich", "ket_qua", "noi_dung",
                  "goi_y", "cau_tra_loi"]:
            if isinstance(d.get(k), str) and d[k].strip():
                van_ban = d[k].strip()
                break

        la_genai = nguon == "genai"
        check(f"POST {duong_dan} dung GenAI that (nguon='genai')",
              st == 200 and la_genai,
              f"status={st}  nguon={nguon!r}" +
              (f"  canh bao={canh_bao}" if canh_bao else ""))
        if van_ban:
            print(f"         tra loi: {van_ban[:130]!r}")
        elif st == 200:
            print(f"         (cac truong co trong data: {list(d.keys())})")

finally:
    if server and server.poll() is None:
        print("\n  Tat server...")
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)

    print("\n" + "=" * 64)
    print(f"  DAT : {ok_count}    HONG: {fail_count}")
    print("=" * 64)
