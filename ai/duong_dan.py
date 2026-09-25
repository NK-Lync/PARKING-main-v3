# ============================================================
# duong_dan.py — neo đường dẫn vào thư mục gốc dự án
# ============================================================
#
# Model và file cấu hình nằm trong dự án, KHÔNG nằm trong thư mục
# đang đứng khi gõ lệnh. Để đường dẫn tương đối thì
# `python app.py` chạy từ thư mục khác sẽ đổ ngay với
# FileNotFoundError, dù file vẫn còn nguyên trong dự án.
# ============================================================

import os


# Thư mục gốc dự án: thư mục chứa app.py, tức thư mục cha của ai/.
GOC_DU_AN = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


def duong_dan(*phan):
    """
    Ghép các thành phần thành đường dẫn tuyệt đối trong dự án.

    Đường dẫn tuyệt đối truyền vào được giữ nguyên (os.path.join
    bỏ qua phần đứng trước khi gặp đường dẫn tuyệt đối).
    """
    return os.path.join(GOC_DU_AN, *phan)
