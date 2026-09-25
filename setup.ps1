#Requires -Version 5.1
<#
    setup.ps1 — Chuẩn bị môi trường chạy XeParking (Windows)

    Cách dùng:
        powershell -ExecutionPolicy Bypass -File .\setup.ps1

    Script này idempotent: chạy lại nhiều lần vẫn an toàn.

    Nếu có thư mục _private\ (clone từ repo PARKING-main-v2-private) thì tự động
    copy .env và model sang. Nếu không có, script tạo .env từ file mẫu và in
    hướng dẫn tự cấu hình.

    Tham số:
        -Force    Ghi đè .env hiện có bằng bản trong _private\.
                  Dùng sau khi `git pull` trong _private\ có .env mới.
#>

param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Step { param($m) Write-Host "`n==> $m" -ForegroundColor Cyan }
function Ok   { param($m) Write-Host "    [OK]  $m" -ForegroundColor Green }
function Warn { param($m) Write-Host "    [!]   $m" -ForegroundColor Yellow }
function Fail { param($m) Write-Host "    [X]   $m" -ForegroundColor Red }

$hasPrivate = Test-Path -LiteralPath '_private'

# --------------------------------------------------------------- 1. Python
Step '1/5  Kiểm tra Python'

$python = $null
foreach ($cand in @('py', 'python', 'python3')) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) {
    Fail 'Không tìm thấy Python. Cài tại https://www.python.org/downloads/'
    exit 1
}
Ok (& $python --version 2>&1)

# ---------------------------------------------------------- 2. Môi trường ảo
Step '2/5  Môi trường ảo và thư viện'

$venvPy = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
if (Test-Path -LiteralPath $venvPy) {
    Ok 'venv đã tồn tại, bỏ qua bước tạo'
} else {
    & $python -m venv venv
    Ok 'Đã tạo venv\'
}

& $venvPy -m pip install --upgrade pip --quiet
Ok 'Đã cập nhật pip'

if (Test-Path -LiteralPath 'requirements.txt') {
    & $venvPy -m pip install -r requirements.txt --quiet
    Ok 'Đã cài đặt requirements.txt'
} else {
    Warn 'Không thấy requirements.txt'
}

# ----------------------------------------------------------------- 3. .env
Step '3/5  Cấu hình .env'

if ($hasPrivate -and (Test-Path -LiteralPath '_private\.env')) {
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '_private\.env' -Destination '.env'
        Ok 'Đã copy .env từ _private\'
    } elseif ($Force) {
        Copy-Item -LiteralPath '_private\.env' -Destination '.env' -Force
        Ok 'Đã ghi đè .env bằng bản trong _private\ (-Force)'
    } else {
        $srcEnv = Get-Content -LiteralPath '_private\.env' -Raw
        $dstEnv = Get-Content -LiteralPath '.env' -Raw
        if ($srcEnv -ne $dstEnv) {
            Warn '.env hiện tại KHÁC với bản trong _private\ — có thể repo private đã có cập nhật.'
            Warn 'Chạy lại để ghi đè:  .\setup.ps1 -Force'
            Warn '(Lưu ý: lệnh này sẽ mất các sửa đổi .env bạn tự làm trên máy.)'
        } else {
            Ok '.env đã khớp với _private\'
        }
    }
} elseif (Test-Path -LiteralPath '.env') {
    Ok '.env đã tồn tại, giữ nguyên'
} else {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
    Warn 'Chưa có _private\.env — đã tạo .env từ file mẫu.'
    Warn 'Mở .env, điền SUPABASE_URL và SUPABASE_KEY rồi chạy lại script.'
}

# ---------------------------------------------------------------- 4. Model
Step '4/5  Model AI'

New-Item -ItemType Directory -Force -Path 'models' | Out-Null

if (Test-Path -LiteralPath '_private\models') {
    $pts = @(Get-ChildItem -LiteralPath '_private\models' -Filter '*.pt' -ErrorAction SilentlyContinue)
    if ($pts.Count -gt 0) {
        foreach ($f in $pts) {
            Copy-Item -LiteralPath $f.FullName -Destination 'models\' -Force
            Ok "Đã copy $($f.Name)"
        }
    } else {
        Warn 'Thư mục _private\models rỗng'
    }
}

if (-not (Test-Path -LiteralPath 'models\license_plate.pt')) {
    Warn 'Thiếu models\license_plate.pt — 2 endpoint /api/parking/ai-entry và'
    Warn '/api/parking/ai-exit sẽ báo lỗi khi gọi. Các phần còn lại vẫn chạy bình thường.'
}

if ((Test-Path -LiteralPath '_private\yolo11n.pt') -and -not (Test-Path -LiteralPath 'yolo11n.pt')) {
    Copy-Item -LiteralPath '_private\yolo11n.pt' -Destination 'yolo11n.pt'
    Ok 'Đã copy yolo11n.pt từ _private\'
}

if (Test-Path -LiteralPath 'yolo11n.pt') {
    Ok 'yolo11n.pt đã có'
} else {
    Ok 'yolo11n.pt sẽ được Ultralytics tự tải ở lần chạy đầu tiên'
}

# ---------------------------------------------------------------- 5. Xong
Step '5/5  Hoàn tất'

Write-Host ''
Write-Host '    Chạy ứng dụng:' -ForegroundColor White
Write-Host '        .\venv\Scripts\Activate.ps1'
Write-Host '        python app.py'
Write-Host '    Rồi mở http://127.0.0.1:5000'
Write-Host ''

if (-not $hasPrivate) {
    Write-Host '    Bạn đang dùng bản PUBLIC (không có _private\).' -ForegroundColor Yellow
    Write-Host '    Cần bản chạy đầy đủ? Xem README.md, mục "Dành cho người trong nhóm".' -ForegroundColor Yellow
    Write-Host ''
}
