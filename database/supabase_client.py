import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Đọc file .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Kiểm tra biến môi trường
if not SUPABASE_URL:
    raise ValueError("Thiếu SUPABASE_URL trong file .env")

if not SUPABASE_KEY:
    raise ValueError("Thiếu SUPABASE_KEY trong file .env")

# Tạo Supabase client
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)