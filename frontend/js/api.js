// ============================================================
// api.js — lớp gọi REST API (fetch wrapper)
// ============================================================

App.api = {
  async request(method, path, body, isFormData) {
    const options = { method, headers: {} };

    if (isFormData) {
      // body là FormData -> trình duyệt tự gắn Content-Type.
      options.body = body;
    } else if (body !== undefined) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }

    let res;
    try {
      res = await fetch(App.config.API_BASE + path, options);
    } catch (err) {
      throw new Error("Không kết nối được máy chủ. Hãy chắc chắn `python app.py` đang chạy.");
    }

    let data = null;
    try {
      data = await res.json();
    } catch (err) {
      data = null;
    }

    if (!res.ok) {
      const msg = (data && data.message) ? data.message : `Lỗi máy chủ (${res.status})`;
      const error = new Error(msg);
      error.status = res.status;
      error.data = data;
      throw error;
    }

    return data;
  },

  get(path) { return this.request("GET", path); },
  post(path, body) { return this.request("POST", path, body); },
  put(path, body) { return this.request("PUT", path, body); },
  del(path) { return this.request("DELETE", path); },
  upload(path, formData) { return this.request("POST", path, formData, true); },
};
