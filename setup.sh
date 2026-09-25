#!/usr/bin/env bash
#
# setup.sh — Chuẩn bị môi trường chạy XeParking (macOS / Linux)
#
# Cách dùng:
#     bash setup.sh [--force]
#
# Script này idempotent: chạy lại nhiều lần vẫn an toàn.
# Nếu có thư mục _private/ (clone từ repo PARKING-main-v2-private) thì tự động
# copy .env và model sang. Nếu không có, script tạo .env từ file mẫu và in
# hướng dẫn tự cấu hình.
#
#     --force   Ghi đè .env hiện có bằng bản trong _private/.
#               Dùng sau khi `git pull` trong _private/ có .env mới.

set -euo pipefail
cd "$(dirname "$0")"

force=0
for arg in ${1+"$@"}; do
    case "$arg" in
        --force|-f) force=1 ;;
    esac
done

step() { printf '\n\033[36m==> %s\033[0m\n' "$1"; }
ok()   { printf '    \033[32m[OK]\033[0m  %s\n' "$1"; }
warn() { printf '    \033[33m[!]\033[0m   %s\n' "$1"; }
fail() { printf '    \033[31m[X]\033[0m   %s\n' "$1"; }

has_private=0
[ -d _private ] && has_private=1

# --------------------------------------------------------------- 1. Python
step '1/5  Kiểm tra Python'

python=""
for cand in python3 python py; do
    if command -v "$cand" >/dev/null 2>&1; then python="$cand"; break; fi
done
if [ -z "$python" ]; then
    fail 'Không tìm thấy Python. Cài tại https://www.python.org/downloads/'
    exit 1
fi
ok "$("$python" --version 2>&1)"

# ---------------------------------------------------------- 2. Môi trường ảo
step '2/5  Môi trường ảo và thư viện'

if [ -x venv/bin/python ]; then
    ok 'venv đã tồn tại, bỏ qua bước tạo'
else
    "$python" -m venv venv
    ok 'Đã tạo venv/'
fi
venv_py="$PWD/venv/bin/python"

"$venv_py" -m pip install --upgrade pip --quiet
ok 'Đã cập nhật pip'

if [ -f requirements.txt ]; then
    "$venv_py" -m pip install -r requirements.txt --quiet
    ok 'Đã cài đặt requirements.txt'
else
    warn 'Không thấy requirements.txt'
fi

# ----------------------------------------------------------------- 3. .env
step '3/5  Cấu hình .env'

if [ "$has_private" -eq 1 ] && [ -f _private/.env ]; then
    if [ ! -f .env ]; then
        cp _private/.env .env
        ok 'Đã copy .env từ _private/'
    elif [ "$force" -eq 1 ]; then
        cp -f _private/.env .env
        ok 'Đã ghi đè .env bằng bản trong _private/ (--force)'
    elif ! cmp -s _private/.env .env; then
        warn '.env hiện tại KHÁC với bản trong _private/ — có thể repo private đã có cập nhật.'
        warn 'Chạy lại để ghi đè:  bash setup.sh --force'
        warn '(Lưu ý: lệnh này sẽ mất các sửa đổi .env bạn tự làm trên máy.)'
    else
        ok '.env đã khớp với _private/'
    fi
elif [ -f .env ]; then
    ok '.env đã tồn tại, giữ nguyên'
else
    cp .env.example .env
    warn 'Chưa có _private/.env — đã tạo .env từ file mẫu.'
    warn 'Mở .env, điền SUPABASE_URL và SUPABASE_KEY rồi chạy lại script.'
fi

# ---------------------------------------------------------------- 4. Model
step '4/5  Model AI'

mkdir -p models

if [ -d _private/models ]; then
    shopt -s nullglob
    pts=(_private/models/*.pt)
    shopt -u nullglob
    if [ ${#pts[@]} -gt 0 ]; then
        for f in "${pts[@]}"; do
            cp -f "$f" models/
            ok "Đã copy $(basename "$f")"
        done
    else
        warn 'Thư mục _private/models rỗng'
    fi
fi

if [ ! -f models/license_plate.pt ]; then
    warn 'Thiếu models/license_plate.pt — 2 endpoint /api/parking/ai-entry và'
    warn '/api/parking/ai-exit sẽ báo lỗi khi gọi. Các phần còn lại vẫn chạy bình thường.'
fi

if [ -f _private/yolo11n.pt ] && [ ! -f yolo11n.pt ]; then
    cp _private/yolo11n.pt yolo11n.pt
    ok 'Đã copy yolo11n.pt từ _private/'
fi

if [ -f yolo11n.pt ]; then
    ok 'yolo11n.pt đã có'
else
    ok 'yolo11n.pt sẽ được Ultralytics tự tải ở lần chạy đầu tiên'
fi

# ---------------------------------------------------------------- 5. Xong
step '5/5  Hoàn tất'

printf '\n    Chạy ứng dụng:\n'
printf '        source venv/bin/activate\n'
printf '        python app.py\n'
printf '    Rồi mở http://127.0.0.1:5000\n\n'

if [ "$has_private" -eq 0 ]; then
    printf '\033[33m    Bạn đang dùng bản PUBLIC (không có _private/).\033[0m\n'
    printf '\033[33m    Cần bản chạy đầy đủ? Xem README.md, mục "Dành cho người trong nhóm".\033[0m\n\n'
fi
