from abc import ABC, abstractmethod


class IAIProvider(ABC):
    """
    Giao diện trừu tượng cho các dịch vụ AI phân tích dữ liệu (GenAI).

    Giao diện này cho phép thay thế linh hoạt mô hình AI
    (GPT-4o, Gemini, Claude...) thông qua thuộc tính `model_name`
    mà không làm thay đổi cấu trúc nghiệp vụ của hệ thống.

    Các phương thức đều chỉ phân tích dữ liệu được hệ thống
    cung cấp và KHÔNG được tự tạo số liệu.
    """

    @abstractmethod
    def sinh_bao_cao_luu_luong(self, data):
        pass

    @abstractmethod
    def phan_tich_gio_cao_diem(self, data):
        pass

    @abstractmethod
    def goi_y_bo_tri_nhan_su(self, data):
        pass

    @abstractmethod
    def hoi_dap_du_lieu(self, question, context):
        pass
