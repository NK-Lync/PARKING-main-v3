# -*- coding: utf-8 -*-
"""
Kiểm tra kết nối Supabase: đọc .env, tạo client, đếm số dòng từng bảng.

Chạy:  python test_supabase.py
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

if not URL:
    print("[LỖI] Thiếu SUPABASE_URL trong file .env")
    raise SystemExit(1)
if not KEY:
    print("[LỖI] Thiếu SUPABASE_KEY trong file .env")
    raise SystemExit(1)

print("URL :", URL)
print("KEY :", (KEY[:24] + "...") if len(KEY) > 24 else KEY)

supabase = create_client(URL, KEY)

TABLES = ["loaixe", "khuvuc", "vitrido", "luotguixe", "vethang", "taikhoan"]

print("\nKết quả kiểm tra từng bảng:")
ok = True
for t in TABLES:
    try:
        resp = supabase.table(t).select("*", count="exact").execute()
        print(f"  [OK]  {t:<12} : {len(resp.data)} dòng")
    except Exception as exc:
        ok = False
        print(f"  [LỖI] {t:<12} : {exc}")

print("\n=> KẾT NỐI THÀNH CÔNG" if ok else "\n=> CÓ LỖI, xem chi tiết ở trên")
