// ============================================================
// views/ai.js — AI hỗ trợ phân tích (GenAI)
// ============================================================

App.views.ai = {
  async render() {
    App.router.setTitle("AI hỗ trợ");
    App.router.setContent(`
      <div class="row g-3 mb-3">
        ${this._actionCard("bao-cao", "Báo cáo lưu lượng", "Tổng hợp số liệu lượt xe gửi thành báo cáo ngắn gọn.", "bi-file-earmark-text")}
        ${this._actionCard("gio-cao-diem", "Phân tích giờ cao điểm", "Xác định khung giờ có lưu lượng xe cao nhất.", "bi-graph-up-arrow")}
        ${this._actionCard("nhan-su", "Gợi ý bố trí nhân sự", "Đề xuất bố trí nhân viên theo lưu lượng.", "bi-people")}
      </div>

      <div class="row g-3">
        <div class="col-lg-5">
          <div class="card h-100">
            <div class="card-header">Hỏi đáp dữ liệu</div>
            <div class="card-body d-flex flex-column">
              <p class="text-muted small">Hỏi về doanh thu, số xe đang gửi, số vị trí hoặc vé tháng.</p>
              <div class="input-group mb-2">
                <input type="text" class="form-control" id="ai-question" placeholder="VD: Hôm nay doanh thu bao nhiêu?">
                <button class="btn btn-primary" id="ai-ask"><i class="bi bi-send"></i> Hỏi</button>
              </div>
              <div id="ai-answer"></div>
            </div>
          </div>
        </div>

        <div class="col-lg-7">
          <div class="card h-100">
            <div class="card-header">Kết quả phân tích</div>
            <div class="card-body">
              <div id="ai-result" class="text-muted">Chọn một phân tích ở trên để bắt đầu.</div>
            </div>
          </div>
        </div>
      </div>`);

    document.getElementById("ai-ask").addEventListener("click", () => this.ask());
    document.getElementById("ai-question").addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.ask();
    });

    ["bao-cao", "gio-cao-diem", "nhan-su"].forEach((k) => {
      document.getElementById(`ai-${k}`).addEventListener("click", () => this.runAction(k));
    });
  },

  _actionCard(key, title, desc, icon) {
    return `
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex align-items-center gap-2 mb-2">
              <i class="bi ${icon} text-primary" style="font-size:1.4rem"></i>
              <h6 class="mb-0">${title}</h6>
            </div>
            <p class="text-muted small flex-grow-1">${desc}</p>
            <button class="btn btn-outline-primary btn-sm" id="ai-${key}"><i class="bi bi-stars me-1"></i>Chạy phân tích</button>
          </div>
        </div>
      </div>`;
  },

  _sourceBadge(r) {
    if (!r || !r.nguon) return "";
    return r.nguon === "genai"
      ? App.ui.badge("Gemini", "primary")
      : App.ui.badge("Phân tích nội bộ", "secondary");
  },

  _renderResult(title, r) {
    const content = r && r.noi_dung ? r.noi_dung : (r && r.cau_tra_loi);
    return `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h6 class="mb-0">${title}</h6>
        ${this._sourceBadge(r)}
      </div>
      <div class="bg-light p-3 rounded" style="white-space:pre-wrap">${App.ui.escape(content || "—")}</div>`;
  },

  async runAction(key) {
    const box = document.getElementById("ai-result");
    box.innerHTML = App.ui.spinner("AI đang phân tích…");
    const map = {
      "bao-cao": ["/api/ai/bao-cao-luu-luong", "Báo cáo lưu lượng"],
      "gio-cao-diem": ["/api/ai/gio-cao-diem", "Phân tích giờ cao điểm"],
      "nhan-su": ["/api/ai/goi-y-nhan-su", "Gợi ý bố trí nhân sự"],
    };
    const [path, title] = map[key];
    try {
      const res = await App.api.post(path);
      box.innerHTML = this._renderResult(title, res.data);
    } catch (err) {
      box.innerHTML = `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  async ask() {
    const input = document.getElementById("ai-question");
    const box = document.getElementById("ai-answer");
    const cauHoi = input.value.trim();
    if (!cauHoi) return;

    box.innerHTML = App.ui.spinner("Đang trả lời…");
    try {
      const res = await App.api.post("/api/ai/hoi-dap", { cau_hoi: cauHoi });
      const r = res.data || {};
      box.innerHTML = `
        <div class="d-flex justify-content-end mb-2">
          <span class="badge text-bg-primary">${App.ui.escape(cauHoi)}</span>
        </div>
        <div class="d-flex justify-content-between align-items-center mb-1">${this._sourceBadge(r)}</div>
        <div class="bg-light p-3 rounded" style="white-space:pre-wrap">${App.ui.escape(r.cau_tra_loi || "—")}</div>`;
    } catch (err) {
      box.innerHTML = `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },
};
