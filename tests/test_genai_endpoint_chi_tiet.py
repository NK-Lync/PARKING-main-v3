# -*- coding: utf-8 -*-
"""
Chay lai 4 endpoint /api/ai/* voi:
  - dung ten truong 'cau_hoi' (lan truoc toi gui sai 'cauhoi' -> 400)
  - nghi 25 giay giua cac lan goi, de loai tru nguyen nhan rate-limit
  - in DAY DU noi dung canh bao loi, khong cat bot
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
MODEL_MOI = "gemini-3.8-flash"
NGHI = 25

server = None


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
    print(f"SERVER voi AI_MODEL_NAME={MODEL_MOI}, nghi {NGHI}s giua cac lan goi")
    print("=" * 64)

    server = subprocess.Popen(
        [_sys.executable, DUONG_DAN_APP],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=GOC_DU_AN,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "AI_MODEL_NAME": MODEL_MOI},
    )

    for _ in range(60):
        time.sleep(0.5)
        if server.poll() is not None:
            print(server.stdout.read().decode("utf-8", "replace")[:1500])
            raise SystemExit(1)
        try:
            urllib.request.urlopen(BASE + "/api/parking/status", timeout=2)
            break
        except urllib.error.HTTPError:
            break
        except Exception:
            continue

    print("Server san sang.\n")

    ket_qua = []

    for i, (duong_dan, body) in enumerate([
        ("/api/ai/bao-cao-luu-luong", None),
        ("/api/ai/gio-cao-diem", None),
        ("/api/ai/goi-y-nhan-su", None),
        ("/api/ai/hoi-dap", {"cau_hoi": "Bai xe hien co bao nhieu cho trong?"}),
    ]):
        if i > 0:
            print(f"  ... nghi {NGHI}s ...\n")
            time.sleep(NGHI)

        st, r = goi("POST", duong_dan, body)
        d = r.get("data") if isinstance(r.get("data"), dict) else {}
        nguon = d.get("nguon")
        canh_bao = d.get("canh_bao")

        print("-" * 64)
        print(f"{duong_dan}   status={st}   nguon={nguon!r}")

        if canh_bao:
            print(f"  CANH BAO DAY DU:\n    {canh_bao}")

        if st != 200:
            print(f"  phan hoi: {json.dumps(r, ensure_ascii=False)[:400]}")

        for k in ["tra_loi", "bao_cao", "phan_tich", "ket_qua", "noi_dung", "goi_y", "cau_tra_loi"]:
            if isinstance(d.get(k), str) and d[k].strip():
                print(f"  {k}: {d[k].strip()[:220]!r}")
                break

        ket_qua.append((duong_dan, st, nguon))
        print()

    print("=" * 64)
    print("TONG KET")
    print("=" * 64)
    for dd, st, ng in ket_qua:
        dau = "GenAI that" if ng == "genai" else ("noi-bo" if ng == "noi-bo" else "?")
        print(f"  {dd:34s} status={st}  nguon={ng!r}  -> {dau}")

finally:
    if server and server.poll() is None:
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)
        print("\n  Da tat server.")
