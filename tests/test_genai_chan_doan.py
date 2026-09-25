# -*- coding: utf-8 -*-
"""
Chan doan tang GenAI: vi sao /api/ai/* luon roi ve 'noi-bo'?

Khong in gia tri AI_API_KEY ra man hinh - chi in do dai va 4 ky tu dau.
"""

import sys
import io
import os
import json
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

from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("AI_API_URL")
MODEL = os.getenv("AI_MODEL_NAME")
KEY = os.getenv("AI_API_KEY")

print("=== CAU HINH ===")
print(f"  AI_API_URL   = {URL}")
print(f"  AI_MODEL_NAME= {MODEL}")
print(f"  AI_API_KEY   = <{len(KEY or '')} ky tu, bat dau { (KEY or '')[:4]!r}>")
print(f"  Tien to 'AIza' (chuan Google AI Studio)? {(KEY or '').startswith('AIza')}")


def goi(url, body=None, method="POST", key=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key if key is not None else KEY}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


print("\n=== 1. LIET KE MODEL MA KEY NAY THAY DUOC ===")
st, body = goi("https://generativelanguage.googleapis.com/v1beta/openai/models",
               method="GET")
print(f"  status = {st}")
print(f"  {body[:700]}")

print("\n=== 2. GOI CHAT/COMPLETIONS Y HET CODE DANG GOI ===")
st, body = goi(URL, {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Tra loi dung mot tu: OK"}],
    "max_tokens": 10,
})
print(f"  status = {st}")
print(f"  {body[:900]}")

print("\n=== 3. THU VAI TEN MODEL KHAC (neu 404 la do sai ten) ===")
for ten in ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash",
            "gemini-flash-latest"]:
    st, body = goi(URL, {
        "model": ten,
        "messages": [{"role": "user", "content": "OK"}],
        "max_tokens": 5,
    })
    dau = ""
    if st == 200:
        try:
            dau = json.loads(body)["choices"][0]["message"]["content"][:40]
        except Exception:
            dau = body[:80]
    else:
        try:
            dau = json.loads(body)["error"]["message"][:110]
        except Exception:
            dau = body[:110]
    print(f"  {ten:22s} status={st}  {dau!r}")
