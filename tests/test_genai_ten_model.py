# -*- coding: utf-8 -*-
"""Thu cac ten model con song, tim ten chay duoc that su."""

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
KEY = os.getenv("AI_API_KEY")


def goi(model):
    req = urllib.request.Request(
        URL,
        data=json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Tra loi ngan: 2+2 bang may?"}],
            "max_tokens": 30,
        }).encode("utf-8"),
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {KEY}")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


UNG_VIEN = [
    "gemini-3.8-flash",
    "models/gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.8-pro",
    "gemini-pro-latest",
    "gemini-2.5-flash-preview-tts",
]

for ten in UNG_VIEN:
    st, body = goi(ten)
    if st == 200:
        try:
            tra_loi = json.loads(body)["choices"][0]["message"]["content"]
            print(f"  [CHAY DUOC] {ten:32s} -> {tra_loi.strip()[:60]!r}")
        except Exception:
            print(f"  [CHAY DUOC] {ten:32s} -> (khong doc duoc noi dung)")
    else:
        try:
            msg = json.loads(body)["error"]["message"][:95]
        except Exception:
            msg = body[:95]
        print(f"  [loi {st}]    {ten:32s} {msg!r}")
