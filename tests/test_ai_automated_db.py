# -*- coding: utf-8 -*-
"""
Script kiểm thử tự động hệ thống AI, kiểm soát qua database và ghi log prompt.
Kiểm tra:
1. Gọi 4 chức năng AI (báo cáo lưu lượng, giờ cao điểm, nhân sự, hỏi đáp).
2. Xác nhận log prompt được lưu vào bảng `ai_prompt_logs` trên Supabase.
3. Kiểm tra cấu hình `ai_system_config`.
"""

import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Cho phép chạy từ bất kỳ thư mục nào
GOC_DU_AN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if GOC_DU_AN not in sys.path:
    sys.path.insert(0, GOC_DU_AN)

from dotenv import load_dotenv
load_dotenv()

from ai.he_thong_ai import HeThongAI
from services.thong_ke_service import ThongKeService
from database.supabase_client import supabase


def test_ai_automation_and_db_logging():
    print("=== BẮT ĐẦU KIỂM THỬ TỰ ĐỘNG AI & DB LOGGING ===")

    # 1. Kiểm tra kết nối Supabase và bảng cấu hình AI
    print("\n--- 1. Kiểm tra bảng `ai_system_config` ---")
    try:
        cfg_res = supabase.table("ai_system_config").select("*").execute()
        print(f"  Thành công đọc cấu hình AI từ DB. Số lượng cấu hình: {len(cfg_res.data)}")
        for row in cfg_res.data:
            print(f"    - {row['config_key']} = {row['config_value']} ({row.get('description')})")
    except Exception as e:
        print(f"  Lỗi đọc `ai_system_config` (có thể chưa chạy migration SQL): {e}")

    # 2. Lấy dữ liệu phân tích từ ThongKeService
    print("\n--- 2. Lấy dữ liệu thống kê đầu vào cho AI ---")
    try:
        data = ThongKeService.du_lieu_phan_tich()
        print(f"  Đã lấy dữ liệu phân tích. Tổng lượt gửi: {data.get('tong_luot_gui')}, Doanh thu: {data.get('tong_doanh_thu')}")
    except Exception as e:
        print(f"  Lỗi lấy dữ liệu thống kê: {e}")
        return

    ai = HeThongAI()

    # 3. Kiểm tra sinh báo cáo lưu lượng
    print("\n--- 3. Kiểm tra `sinh_bao_cao_luu_luong` ---")
    res_bc = ai.sinh_bao_cao_luu_luong(data)
    print(f"  Kết quả: success={res_bc.get('success')}, nguồn={res_bc.get('nguon')}")
    print(f"  Nội dung: {res_bc.get('noi_dung', '')[:150]}...")
    if 'canh_bao' in res_bc:
        print(f"  Cảnh báo: {res_bc['canh_bao']}")

    # 4. Kiểm tra phân tích giờ cao điểm
    print("\n--- 4. Kiểm tra `phan_tich_gio_cao_diem` ---")
    res_gcd = ai.phan_tich_gio_cao_diem(data)
    print(f"  Kết quả: success={res_gcd.get('success')}, nguồn={res_gcd.get('nguon')}")
    print(f"  Nội dung: {res_gcd.get('noi_dung', '')[:150]}...")

    # 5. Kiểm tra gợi ý bố trí nhân sự
    print("\n--- 5. Kiểm tra `goi_y_bo_tri_nhan_su` ---")
    res_ns = ai.goi_y_bo_tri_nhan_su(data)
    print(f"  Kết quả: success={res_ns.get('success')}, nguồn={res_ns.get('nguon')}")
    print(f"  Nội dung: {res_ns.get('noi_dung', '')[:150]}...")

    # 6. Kiểm tra hỏi đáp dữ liệu
    print("\n--- 6. Kiểm tra `hoi_dap_du_lieu` ---")
    question = "Tổng doanh thu hiện tại là bao nhiêu?"
    res_hd = ai.hoi_dap_du_lieu(question, data)
    print(f"  Câu hỏi: {question}")
    print(f"  Kết quả: success={res_hd.get('success')}, nguồn={res_hd.get('nguon')}")
    print(f"  Trả lời: {res_hd.get('cau_tra_loi', '')}")

    # 7. Kiểm tra lịch sử prompt được lưu trong `ai_prompt_logs`
    print("\n--- 7. Kiểm tra bảng `ai_prompt_logs` trên DB ---")
    try:
        logs_res = supabase.table("ai_prompt_logs").select("*").order("created_at", desc=True).limit(5).execute()
        print(f"  Đã ghi nhận {len(logs_res.data)} bản ghi prompt gần nhất trong DB:")
        for log in logs_res.data:
            print(f"    - [{log['created_at']}] Loại: {log['prompt_type']} | Trạng thái: {log['status']} | Model: {log['model_name']}")
    except Exception as e:
        print(f"  Lỗi đọc `ai_prompt_logs`: {e}")

    print("\n=== HOÀN TẤT KIỂM THỬ TỰ ĐỘNG AI & DB LOGGING ===")


if __name__ == "__main__":
    test_ai_automation_and_db_logging()
