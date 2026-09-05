import json
import os

import requests

from ai.iai_provider import IAIProvider


class HeThongAI(IAIProvider):
    """
    Dịch vụ AI phân tích dữ liệu (GenAI) của hệ thống XeParking.

    Triển khai giao diện IAIProvider. Sử dụng một endpoint
    OpenAI-compatible (chat/completions) để sinh báo cáo và
    trả lời câu hỏi dựa trên dữ liệu do hệ thống cung cấp.

    Cấu hình qua biến môi trường (file .env):

        AI_API_URL   = https://api.openai.com/v1/chat/completions
        AI_API_KEY   = <khóa API>
        AI_MODEL_NAME = gpt-4o

    Khi KHÔNG có API key, dịch vụ tự động chuyển sang chế độ
    "phân tích nội bộ" (deterministic) để hệ thống vẫn hoạt
    động mà không cần kết nối mạng hay khóa API.
    """

    def __init__(self):
        self.api_url = os.getenv(
            "AI_API_URL",
            "https://api.openai.com/v1/chat/completions"
        )

        self.api_key = os.getenv("AI_API_KEY", "")

        self.model_name = os.getenv(
            "AI_MODEL_NAME",
            "gpt-4o"
        )

    # ============================================================
    # GỌI API CHAT COMPLETIONS
    # ============================================================
    def _chat(self, system_prompt, user_prompt):
        if not self.api_key:
            return None

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30
            )

            response.raise_for_status()

            payload = response.json()

            return (
                payload["choices"][0]["message"]["content"]
                .strip()
            )

        except Exception:
            return None

    # ============================================================
    # IAIProvider: SINH BÁO CÁO LƯU LƯỢNG
    # ============================================================
    def sinh_bao_cao_luu_luong(self, data):
        system_prompt = (
            "Bạn là trợ lý phân tích dữ liệu bãi đỗ xe. "
            "Chỉ dựa vào số liệu được cung cấp, không tự bịa số. "
            "Trả lời bằng tiếng Việt."
        )

        user_prompt = (
            "Hãy viết báo cáo lưu lượng xe gửi dựa trên dữ liệu sau:\n"
            f"{json.dumps(data, ensure_ascii=False)}"
        )

        genai_text = self._chat(system_prompt, user_prompt)

        if genai_text:
            return {
                "success": True,
                "nguon": "genai",
                "model": self.model_name,
                "noi_dung": genai_text
            }

        # Fallback nội bộ (không cần API).
        tong_luot = data.get("tong_luot_gui", 0)

        return {
            "success": True,
            "nguon": "noi-bo",
            "model": self.model_name,
            "noi_dung": (
                f"Báo cáo lưu lượng: hệ thống ghi nhận "
                f"tổng cộng {tong_luot} lượt gửi xe. "
                "Số liệu này được tổng hợp trực tiếp từ "
                "dữ liệu nghiệp vụ lưu trữ trên hệ thống."
            )
        }

    # ============================================================
    # IAIProvider: PHÂN TÍCH GIỜ CAO ĐIỂM
    # ============================================================
    def phan_tich_gio_cao_diem(self, data):
        system_prompt = (
            "Bạn là chuyên gia phân tích giao thông bãi đỗ xe. "
            "Chỉ dựa vào số liệu được cung cấp. "
            "Trả lời bằng tiếng Việt."
        )

        user_prompt = (
            "Hãy phân tích giờ cao điểm dựa trên lưu lượng "
            "theo giờ sau:\n"
            f"{json.dumps(data, ensure_ascii=False)}"
        )

        genai_text = self._chat(system_prompt, user_prompt)

        if genai_text:
            return {
                "success": True,
                "nguon": "genai",
                "model": self.model_name,
                "noi_dung": genai_text
            }

        # Fallback nội bộ: tìm giờ có lượt gửi cao nhất.
        theo_gio = data.get("luu_luong_theo_gio", {})

        if theo_gio:
            gio_cao_diem = max(theo_gio, key=theo_gio.get)
            so_luot = theo_gio[gio_cao_diem]

            noi_dung = (
                f"Giờ cao điểm là {gio_cao_diem}:00 với "
                f"{so_luot} lượt xe gửi, cao nhất trong ngày."
            )
        else:
            noi_dung = (
                "Chưa đủ dữ liệu để xác định giờ cao điểm."
            )

        return {
            "success": True,
            "nguon": "noi-bo",
            "model": self.model_name,
            "noi_dung": noi_dung
        }

    # ============================================================
    # IAIProvider: GỢI Ý BỐ TRÍ NHÂN SỰ
    # ============================================================
    def goi_y_bo_tri_nhan_su(self, data):
        system_prompt = (
            "Bạn là chuyên gia vận hành bãi đỗ xe. "
            "Đề xuất bố trí nhân sự dựa trên số liệu được cung cấp. "
            "Trả lời bằng tiếng Việt."
        )

        user_prompt = (
            "Hãy gợi ý bố trí nhân sự dựa trên dữ liệu sau:\n"
            f"{json.dumps(data, ensure_ascii=False)}"
        )

        genai_text = self._chat(system_prompt, user_prompt)

        if genai_text:
            return {
                "success": True,
                "nguon": "genai",
                "model": self.model_name,
                "noi_dung": genai_text
            }

        # Fallback nội bộ: gợi ý theo quy tắc đơn giản.
        theo_gio = data.get("luu_luong_theo_gio", {})

        if theo_gio:
            gio_cao_diem = max(theo_gio, key=theo_gio.get)
            noi_dung = (
                f"Nên bố trí thêm nhân viên vào khung giờ "
                f"{gio_cao_diem}:00 - {gio_cao_diem + 1}:00 "
                "do đây là thời điểm có lưu lượng xe cao nhất."
            )
        else:
            noi_dung = (
                "Chưa đủ dữ liệu để gợi ý bố trí nhân sự."
            )

        return {
            "success": True,
            "nguon": "noi-bo",
            "model": self.model_name,
            "noi_dung": noi_dung
        }

    # ============================================================
    # IAIProvider: HỎI ĐÁP DỮ LIỆU
    # ============================================================
    def hoi_dap_du_lieu(self, question, context):
        system_prompt = (
            "Bạn là trợ lý hỏi đáp về hệ thống bãi đỗ xe. "
            "Chỉ trả lời dựa trên ngữ cảnh dữ liệu được cung cấp. "
            "Trả lời bằng tiếng Việt."
        )

        user_prompt = (
            f"Câu hỏi: {question}\n\n"
            f"Ngữ cảnh dữ liệu:\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )

        genai_text = self._chat(system_prompt, user_prompt)

        if genai_text:
            return {
                "success": True,
                "nguon": "genai",
                "model": self.model_name,
                "cau_hoi": question,
                "cau_tra_loi": genai_text
            }

        # Fallback nội bộ: trả lời theo từ khóa đơn giản.
        cau_tra_loi = self._tra_loi_noi_bo(question, context)

        return {
            "success": True,
            "nguon": "noi-bo",
            "model": self.model_name,
            "cau_hoi": question,
            "cau_tra_loi": cau_tra_loi
        }

    def _tra_loi_noi_bo(self, question, context):
        q = question.lower()

        if "doanh thu" in q:
            return (
                f"Tổng doanh thu hiện tại là "
                f"{context.get('tong_doanh_thu', 0)} VNĐ."
            )

        if "đang gửi" in q or "đang có xe" in q:
            return (
                f"Hiện có {context.get('so_xe_dang_gui', 0)} "
                "xe đang gửi trong bãi."
            )

        if "vị trí" in q or "chỗ" in q:
            return (
                f"Bãi có tổng cộng "
                f"{context.get('tong_so_vi_tri', 0)} vị trí đỗ."
            )

        if "vé tháng" in q:
            return (
                f"Có {context.get('so_ve_thang_hieu_luc', 0)} "
                "vé tháng còn hiệu lực."
            )

        return (
            "Hệ thống chưa đủ thông tin để trả lời câu hỏi này. "
            "Vui lòng hỏi về doanh thu, số xe đang gửi, "
            "số vị trí hoặc vé tháng."
        )
